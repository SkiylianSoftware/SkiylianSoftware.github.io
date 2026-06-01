export default [
  {
    files: ["assets/js/*.js"],
    languageOptions: {
      ecmaVersion: 5,
      sourceType: "script",
      globals: {
        document: "readonly",
        window: "readonly",
        console: "readonly",
        openPlayer: "readonly",
        randomVideo: "readonly",
        filterSeries: "readonly",
        parseChapters: "readonly",
        findWatchNext: "readonly",
      },
    },
    rules: {
      "no-var": "off",
      "prefer-const": "off",
      "no-unused-vars": ["error", {
        args: "none",
        varsIgnorePattern: "^(randomVideo|filterSeries|parseChapters|findWatchNext|toggleMoreFilters)$",
      }],
    },
  },
];