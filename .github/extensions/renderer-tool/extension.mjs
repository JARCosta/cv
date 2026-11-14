// Extension: renderer-tool
// Tool to run repository renderer (scripts/render_resume.py) and return JSON metadata

import { joinSession } from "@github/copilot-sdk/extension";
import { fileURLToPath } from "url";
import path from "path";
import fs from "fs";
import { execFile } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function runRendererTool(draftPath) {
  return new Promise((resolve, reject) => {
    const pythonExe = process.env.PYTHON || "python";
    const resolvedDraftPath = path.resolve(draftPath);
    const scriptPath = path.join(
      __dirname,
      "..",
      "..",
      "scripts",
      "run_renderer_tool.py"
    );

    execFile(pythonExe, [scriptPath, resolvedDraftPath, "--json"], (error, stdout, stderr) => {
      if (error) {
        reject(new Error(`Renderer tool failed: ${error.message}\n${stderr}`));
        return;
      }
      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (e) {
        reject(new Error(`Failed to parse renderer JSON output: ${e.message}\nOutput was: ${stdout}`));
      }
    });
  });
}

const session = await joinSession({
  tools: [
    {
      name: "renderer-tool",
      description: "Run the local render_resume.py script on a Markdown draft and return JSON metadata.",
      parameters: {
        type: "object",
        properties: {
          draftPath: { type: "string", description: "Path to the Markdown draft to render." },
        },
        required: ["draftPath"],
      },
      handler: async ({ draftPath }) => {
        if (!fs.existsSync(draftPath)) {
          return { success: false, error: `Draft file not found: ${draftPath}` };
        }
        try {
          const result = await runRendererTool(draftPath);
          return result;
        } catch (error) {
          return { success: false, error: error.message };
        }
      },
    },
  ],
});

