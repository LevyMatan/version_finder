import globals from "globals";
import pluginJs from "@eslint/js";

export default [
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.jest,
        bootstrap: "readonly",
      },
    },
    rules: {
      "require-await": "error", // Ensure this rule is within the `rules` object
    },
  },
  pluginJs.configs.recommended,
  // If you have other configurations that should include the `require-await` rule,
  // ensure it's added within their `rules` object as well.
];
