# Architecture and maintenance

## Runtime boundaries

The application shell is plain HTML/CSS/JavaScript. CodeMirror manages editable source; `core.js` is a side-effect-free UMD module used by both browser code and Node regression tests. No remote services or accounts participate in rendering or persistence.

`app.js` creates an off-screen iframe with `sandbox="allow-scripts"` and deliberately omits `allow-same-origin`. The iframe loads only the pinned Mermaid bundle and `renderer.js`. The portable edition uses equivalent embedded `srcdoc`. Messages are accepted only from the expected iframe/parent and are associated with render-job identifiers. The parent serializes render requests, coalesces pending edits, and rejects mismatched responses.

Mermaid parses and renders source inside that frame. Strict security and a configuration allowlist constrain options. A second SVG pass removes executable/event content, external references, and rich HTML, supplies explicit dimensions, and normalizes character references only in text nodes. The parent uses a Blob-backed `<img>`, rather than injecting an interactive SVG document into its application DOM. SVG exports optionally embed source metadata; PNG uses the sanitized SVG through a canvas.

The worker is an offline **application-asset cache**, not a diagram-storage mechanism. It has a path-scoped versioned cache, does not intercept unrelated URLs, and does not store user imports or exports. It intentionally does not activate an update over an existing open session via `skipWaiting()`.

## State and recovery

Storage key: `gsg-mermaid-workbench-v1`. Recovery key: the same key plus `-recovery`. JSON format: `gsg-mermaid-workspace`; schema version: `1`. Workspace revisions are independent random identifiers, not application versions. State is reconstructed through explicit validators rather than merged indiscriminately into executable configuration.

A workspace contains document IDs, source, titles, appearance, notes, tags/collections, review registers, snapshots, baseline selection, and a last-valid source/appearance pair. Last-valid images are an in-memory cache; after a reload the app can reconstruct the previous valid view from that stored pair when the current source or configuration is invalid.

Autosave is debounced. A revision check prevents an ordinary stale tab from overwriting a newly observed revision. Web Locks serialize writes where the browser supplies that API. Where Web Locks are unavailable, revision checks and storage events are best-effort rather than a database transaction. Prefer one actively editing tab. The conflict dialog offers explicit preservation/replacement choices; no automated semantic merge is attempted.

Imported JSON uses the same validators. Unsupported workspace versions and oversized documents fail without replacing current data. Merging creates fresh document IDs. Snapshot pruning preserves a selected baseline. Raw Mermaid source is authoritative; no attempt is made to reverse-engineer ordinary SVG or PNG pixels into editable Mermaid.

## Storage privacy

Browser storage is not encrypted by this application. Anyone with access to the browser profile, same-origin application scripts, or exported files may be able to read the data. A sandboxed renderer does not make the entire hosting origin trustworthy. Use an appropriate private origin/browser profile for sensitive diagrams and export encrypted backups through an external workflow when necessary.

No application telemetry, cloud uploads, collaboration backend, or automatic external image downloads exist. Normal hosting access logs and browser/vendor behavior are outside this application’s controls.

## Release procedure

1. Edit the readable static sources and bump visible application version, core version, worker cache version, manifest description, output filename, and documentation together.
2. Preserve schema compatibility or provide an explicit migration with tests; never reuse a schema number for incompatible data.
3. Run `node --test tests/*.test.cjs`.
4. Build the portable edition with `python3 scripts/build_release.py` and run both browser regression scripts.
5. Review desktop/mobile/high-contrast/error/export screenshots, and validate the release on the actual target browser and hosting origin.
6. Test first-load install, offline reopen, cache upgrade, JSON backup/restore, native downloads, print-to-PDF, and storage persistence on that origin.
7. Rebuild checksums after final documentation/assets are included; package a complete, internally consistent directory. Do not merge old and new runtime files.

The portable builder is standard-library Python and resolves all inputs from this repository. Normal runtime and hosting do not require it. It embeds notices as non-executable plain text. The source ZIP and `checksums.json` make a specific release inspectable.

## Pinned vendor provenance

The build environment could not download package-registry assets directly. It did contain Gradio 6.5.1’s already-installed frontend distribution, including Mermaid 11.12.2. The recovery script traced its local imports, replaced Vite preload/shared helpers with minimal local equivalents, removed unrelated Svelte imports, and transpiled the 66-module graph into a local registry bundle. It does not include the Gradio application, cloud APIs, telemetry, fonts, or external module requests.

`vendor/provenance.json` records the source module names and transformations. `prepare-local-vendor.cjs` takes the matching asset directory as its first argument and obtains TypeScript from `require('typescript')`, or the `TYPESCRIPT_PATH` environment override. The entry module/export names are specific to that distribution; a different release requires a deliberate adapter and full regression pass. The resulting checked-in `vendor/mermaid.bundle.js` is sufficient for runtime use.

Not every transitive version was recoverable from the distribution. The notices identify the upstream projects but do not constitute a fully versioned or security-audited software bill of materials. Do not describe this as an unmodified npm package or as the latest Mermaid. Future engine upgrades should obtain official pinned upstream artifacts, retain notices, and repeat the compatibility/security tests.

## Known v1 boundaries

Source-first authoring; guided controls are limited to explicit flowchart declarations. No arbitrary node dragging, visual graph-to-source parser, collaborative live editing, ELK plugin, ZenUML, external icon registry, remote fetch/import, AI generation, or batch-image rendering is implemented. Browser PDF output is through its print interface, not an independent PDF engine. Findings express an author’s assessment; a successful Mermaid parse does not establish factual truth.
