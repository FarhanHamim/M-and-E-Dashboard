import fs from 'fs/promises';
import path from 'path';
import postcss from 'postcss';
import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';

const root = path.resolve(process.cwd());
const inputPath = path.join(root, 'static', 'src', 'tailwind.css');
const outputDir = path.join(root, 'static', 'css');
const outputPath = path.join(outputDir, 'tailwind.css');

async function build() {
  const css = await fs.readFile(inputPath, 'utf8');
  const result = await postcss([tailwindcss({ config: path.join(root, 'tailwind.config.js') }), autoprefixer]).process(css, {
    from: inputPath,
    to: outputPath,
  });
  await fs.mkdir(outputDir, { recursive: true });
  await fs.writeFile(outputPath, result.css, 'utf8');
  if (result.map) {
    await fs.writeFile(outputPath + '.map', result.map.toString(), 'utf8');
  }
  console.log('Tailwind CSS built to', outputPath);
}

build().catch((err) => {
  console.error(err);
  process.exit(1);
});


