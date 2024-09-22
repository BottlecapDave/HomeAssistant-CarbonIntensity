import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const manifestFilePath = join(__dirname, '../custom_components/carbon_intensity/manifest.json');

function updateManifestVersion(version: string) {
  const buffer = readFileSync(manifestFilePath);
  const content = JSON.parse(buffer.toString());
  content.version = version;

  writeFileSync(manifestFilePath, JSON.stringify(content, null, 2));
  console.log(`Updated manifest version to '${version}'`);
}

updateManifestVersion(process.argv[2]);