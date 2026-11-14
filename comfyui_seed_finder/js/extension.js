import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import "./seed-finder.js";

app.registerExtension({
  name: "AIWorkbench.SeedFinder",
  setup() {
    globalThis.ComfySeedFinder.mount(() => api.fetchApi("/history", { method: "GET", cache: "no-store" }));
  },
});
