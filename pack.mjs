// Packer for news-image-20261120.
// Reads entry.png, base64-encodes it, and injects the result into
// main.ts as the PAYLOAD constant on exactly one line. The hand-written
// main.ts carries a "__PAYLOAD__" placeholder on first pack; on later
// runs the existing payload line is replaced in place, so packing is
// idempotent and never touches the rest of the program.
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const mainPath = join(here, "main.ts");

const encoded = readFileSync(join(here, "entry.png")).toString("base64");
if (encoded.length === 0 || encoded.includes("\n")) {
  throw new Error("base64 encoding failed or wrapped");
}

const source = readFileSync(mainPath, "utf8");
const payloadLine = `const PAYLOAD = "${encoded}";`;
const linePattern = /^const PAYLOAD = ".*";$/m;
if (!linePattern.test(source)) {
  throw new Error("no PAYLOAD line found in main.ts to replace");
}
const packed = source.replace(linePattern, payloadLine);
writeFileSync(mainPath, packed);
console.log(`packed ${encoded.length} base64 chars into main.ts`);
