module.exports = {
  // Permitimos las at-rules que Tailwind usa durante el build para evitar
  // falsos positivos en stylelint (ej: @tailwind, @apply, @layer, @screen).
  rules: {
    'at-rule-no-unknown': [
      true,
      {
        ignoreAtRules: ['tailwind', 'apply', 'variants', 'responsive', 'screen', 'layer']
      }
    ]
  }
};
