# MERMAID Workbench v1.0.0 — verification report

**Date:** 17 September 2026  
**Build:** self-contained HTML and the corresponding checked-in static sources  
**Engine:** bundled Mermaid 11.12.2  
**Environment:** Chromium 144.0.7559.96 on Debian 13; Node 22.16.0; Python Playwright

## Results

| Suite | Result | Meaning |
|---|---:|---|
| Node core and static tests | 38 passed, 0 failed | 31 data-model/validation/import/history assertions and 7 static asset, cache-handler, and packaging assertions |
| Browser workflow suite | 62 passed, 0 failed | Working UI paths, real sandboxed rendering, recovery, generated exports, and responsive layouts |
| Renderer matrix | 129 passed, 0 failed | 24 templates × 5 palettes, plus 9 error, security-regression, Unicode, and larger-diagram fixtures |

No uncaught errors were recorded during either browser suite's observation window. These counts describe the included regression checks, not exhaustive coverage or a security certification. A rendering fixture passes only when its expected outcome occurs; rejection is the expected outcome for invalid or unsafe inputs.

Machine-readable evidence is included in `tests/browser-results.json` and `tests/renderer-results.json`. The scripts are also included so maintainers can rerun and extend the checks.

## What ran for real

The browser suite loaded the complete portable HTML, including the actual editor and bundled Mermaid renderer. It did not substitute an image, a parser mock, or a fake rendering engine. The iframe retained its production sandbox and content-security policy.

The suite exercised initial rendering; template search; source editing and manual rendering; creation, duplication, deletion, and undo; guided flowchart nodes and edges; named snapshots, baseline comparison, and restore; notes and review registers; appearance changes; invalid configuration rejection; and typed-confirmation Fresh Start.

Recovery tests deliberately introduced a syntax error and checked that the prior good preview survived. Stale SVG/PNG exports were blocked by default. After explicit permission, a last-valid SVG had a marked filename and metadata containing the actual prior source. Corrected source recovered without losing the diagram. Quota failures, storage denial, corrupt stored data, and an incoming revision conflict were exercised; failed imports did not replace the workspace.

Export tests inspected the generated SVG and its editable-source metadata, produced a real PNG with a valid PNG signature, decoded the report's embedded image, opened the actual generated ZIP with JSZip, checked source/Markdown/JSON/HTML payloads, and round-tripped exported SVG source. The oversized PNG guard was exercised. These were real generated files in memory, not confirmation-message-only tests.

The renderer matrix covered all 24 templates in Paper, Forest, Ocean, Night, and Monochrome palettes. Each successful SVG was parsed, checked for prohibited active/external content, and decoded as an image. Additional fixtures covered invalid source, source-length limits, forbidden configuration, prototype-related configuration, unsafe links, HTML labels, source-level security directives, Unicode, and a 200-node chain. This is a bounded stress fixture, not a general large-diagram performance guarantee.

## Visual review

The desktop workbench, syntax-error state, mobile preview, and actual exported PNG were inspected. Quoted labels initially showed entity names instead of quotation marks; that defect was corrected in SVG text-node normalization and covered by a regression assertion. Requirements and C4 template problems were also corrected before the final matrix pass.

Screenshots in `docs/` show the desktop workbench, template gallery, inspector, error recovery, light theme, high-contrast theme, and mobile source/preview layouts. Desktop capture used a 1512 × 982 viewport; mobile layout checks used 390 × 844. The browser suite verified no horizontal page overflow at that mobile size and a fitting inspector. Viewport emulation is not a physical-device or assistive-technology audit.

## Test-environment limitations

Browser policy in the build environment did not permit ordinary navigation to a local web origin. Tests therefore used Playwright's `set_content()` on an `about:blank` page. No browser or enterprise policies were changed.

**Storage:** most workflow tests supplied an explicit in-memory `localStorage` shim. The suite verified serialization, rehydration in a new page, simulated quota failures, a simulated incoming revision, and recovery decisions. It also ran the real denied-storage path without the shim. This does **not** establish persistence on a particular `file://` or HTTPS origin, survival across browser restarts, or real multi-tab Web Locks behavior.

**Downloads:** tests intercepted object URLs and anchor clicks to inspect actual generated Blobs. They did not exercise a native save dialog, download-folder permissions, or a successful OS-level file save. The clipboard fallback was exercised; system clipboard permission behavior was not certified.

**Offline hosting:** runtime assets are packaged locally and the portable application rendered with no HTTP requests observed during the suite's observation window. The service-worker tests used mocked cache/events to check scope, registration handlers, and asset declarations. Actual registration, installability, cache upgrades, and offline reopening on a real HTTPS/localhost origin were not exercised.

**Printing and browser coverage:** HTML report content and image decoding were tested. Native print/PDF output, Safari, Firefox, browser extensions, physical mobile touch gestures, and screen-reader interaction remain unverified. Presentation mode is an application layout; it is not a claim that the browser fullscreen API was tested.

## Recommended acceptance checks on the target browser

Before relying on this release for important work, open the portable HTML in the intended browser and create a disposable diagram. Export and reimport its workspace JSON, download SVG and PNG, and open those downloads. Close and reopen the application to confirm local storage behavior. Test printing a report and confirm its page breaks.

For a hosted edition, also verify a complete first load, the offline-cache-ready notification, offline reopening, and an upgrade from the prior deployed version. Open two editing tabs and check the conflict workflow. Preserve an independent workspace JSON backup before a deployment or storage change.

The included safeguards reduce accidental loss and unsafe rendering exposure. They do not replace backups, an independent security review, or validation on the actual deployment platform.

## Reproduce

Normal use requires no build or dependency installation. Development tests require their named tools:

```sh
node --test tests/*.test.cjs
python3 scripts/build_release.py
CHROMIUM=/path/to/chromium python3 tests/browser.test.py
CHROMIUM=/path/to/chromium python3 tests/renderer.test.py
```

Use Python Playwright with an installed Chromium. Omit `CHROMIUM` to use Playwright's configured browser. Rebuild checksums after rerunning tests because screenshots and evidence may change.
