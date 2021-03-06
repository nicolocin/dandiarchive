module.exports = {
  preset: 'jest-puppeteer',
  // jest-puppeteer manages the testEnvironment variable, so be sure not to specify it

  setupFilesAfterEnv: [
    // Normally, expect-puppeteer is specified by the jest-puppeteer preset
    'expect-puppeteer',
    'jest-puppeteer-vuetify',
    './jest.setup.js',
  ],

  transformIgnorePatterns: [
    // Apply Babel transformation to jest-puppeteer-vuetify
    'node_modules/(?!jest-puppeteer-vuetify/)',
  ],

  // extend test timeout to 1 hour when debugging
  testTimeout: (process.env.DEBUG === 'true') ? 3600000 : 180000,
};
