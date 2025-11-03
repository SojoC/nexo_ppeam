const fs = require('fs');
const path = require('path');
const postcss = require('postcss');

async function run() {
  const inputPath = path.resolve(__dirname, '..', 'src', 'index.css');
  const outputPath = path.resolve(__dirname, '..', 'src', '.tailwind-output.css');

  if (!fs.existsSync(inputPath)) {
    console.error('Input CSS not found:', inputPath);
    process.exit(1);
  }

  const css = fs.readFileSync(inputPath, 'utf8');

  const tailwindPlugin = require('@tailwindcss/postcss');
  const autoprefixer = require('autoprefixer');

  try {
    const result = await postcss([tailwindPlugin(), autoprefixer()]).process(css, {
      from: inputPath,
      to: outputPath,
      map: false,
    });

    fs.writeFileSync(outputPath, result.css, 'utf8');
    console.log('Wrote', outputPath);
  } catch (err) {
    console.error('CSS build failed:', err);
    process.exit(2);
  }
}

run();
