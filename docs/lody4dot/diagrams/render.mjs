// Export trusted local documentation with temporary, externally installed tools.
import fs from "node:fs/promises";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const directory = path.dirname(fileURLToPath(import.meta.url));
const toolDirectory = process.argv[2];
if (!toolDirectory) throw new Error("Pass the temporary Mermaid/Puppeteer tool directory.");
const requireTool = createRequire(path.resolve(toolDirectory, "package.json"));
const { default: puppeteer } = requireTool("puppeteer-core");
const mermaidDist = path.dirname(requireTool.resolve("mermaid"));
const config = JSON.parse(await fs.readFile(path.join(directory, "mermaid-config.json"), "utf8"));
const known = ["environment-context", "environment-permissions", "environment-lifecycle"];
const names = process.argv.length > 3 ? process.argv.slice(3) : known;
if (names.some(name => !known.includes(name))) throw new Error("Unknown documentation diagram.");

const server = http.createServer(async (request, response) => {
  try {
    const url = new URL(request.url, "http://127.0.0.1");
    if (url.pathname === "/") {
      response.setHeader("Content-Type", "text/html; charset=utf-8");
      response.end('<!doctype html><meta charset="utf-8"><div id="mount"></div>' +
        '<script type="module">import mermaid from "/mermaid/mermaid.esm.min.mjs";' +
        "window.mermaid = mermaid;</script>");
      return;
    }
    if (!url.pathname.startsWith("/mermaid/")) {
      response.writeHead(404).end();
      return;
    }
    const file = path.resolve(mermaidDist, decodeURIComponent(url.pathname.slice(9)));
    if (!file.startsWith(mermaidDist + path.sep)) {
      response.writeHead(403).end();
      return;
    }
    response.setHeader("Content-Type", "text/javascript; charset=utf-8");
    response.end(await fs.readFile(file));
  } catch {
    response.writeHead(404).end();
  }
});

await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const profile = await fs.mkdtemp(path.join(os.tmpdir(), "lody4dot-diagram-browser-"));
const browserEnv = { ...process.env };
delete browserEnv.LODY_CLI_TOKEN;
delete browserEnv.GITEE_ACCESS_TOKEN;
browserEnv.XDG_CONFIG_HOME = path.join(profile, "config");
browserEnv.XDG_CACHE_HOME = path.join(profile, "cache");
let browser;
try {
  browser = await puppeteer.launch({
    executablePath: "/usr/bin/chromium",
    headless: true,
    userDataDir: path.join(profile, "profile"),
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
    env: browserEnv,
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1800, height: 1500, deviceScaleFactor: 1 });
  await page.setRequestInterception(true);
  page.on("request", request => {
    if (new URL(request.url()).origin === origin) request.continue();
    else request.abort();
  });
  await page.goto(origin, { waitUntil: "networkidle0" });
  await page.waitForFunction("window.mermaid !== undefined");
  for (const name of names) {
    const source = await fs.readFile(path.join(directory, `${name}.mmd`), "utf8");
    const rendered = await page.evaluate(async ({ name, source, config }) => {
      window.mermaid.initialize(config);
      await window.mermaid.parse(source);
      const { svg } = await window.mermaid.render(name, source);
      document.getElementById("mount").innerHTML = svg;
      await document.fonts.ready;
      const element = document.querySelector("#mount svg");
      element.setAttribute("width", String(element.viewBox.baseVal.width));
      element.setAttribute("height", String(element.viewBox.baseVal.height));
      element.style.backgroundColor = "#fff";
      return element.outerHTML;
    }, { name, source, config });
    await fs.writeFile(path.join(directory, `${name}.svg`), rendered + "\n");
    console.log(`Rendered ${name}.svg`);
  }
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
  await fs.rm(profile, { recursive: true, force: true });
}
