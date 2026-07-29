import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// Static site deployed to the GitHub user page at the domain root
// https://matteucci.github.io/ (repo: matteucci.github.io), so
// base is '/'. Only set a sub-path base if deploying under a project page.
export default defineConfig({
  site: 'https://matteucci.github.io',
  base: '/',
  output: 'static',
  // applyBaseStyles:false — our global.css owns the @tailwind directives.
  integrations: [tailwind({ applyBaseStyles: false })],
});
