# Decisions worth making before KeMonate grows

The core opportunity is preservation with community agency. Success should be measured by what communities can recover, control and pass on, not only by uploads or AI-generated content.

## Priorities

| Decision | Why it matters | Current implementation / next step |
| --- | --- | --- |
| Informed, revocable consent | Recording, AI processing and public sharing are different permissions. | Separate AI and publication flags; publish/withdraw actions; next: signed or recorded consent evidence, translated consent and consent expiry. |
| Community authority and restricted knowledge | A contributor may not have authority to publish sacred or collective knowledge. | Restriction notes block publishing; next: community roles, review panels and configurable access rules. |
| Rights and reuse | Owning a recording does not automatically confer music, artwork or interview rights. | Attribution and permission attestations; next: explicit licences, rights-holder records, permitted uses and a separate AI-training policy. |
| Translation quality | Local names, idioms and code-switching can be mistranscribed. | Original text stays separate; review resets after AI edits; next: fluent reviewers, time-coded corrections and measured language coverage. |
| Safety and privacy | Stories may expose people, minors, homes or sensitive experiences. | Private by default and broad locations; next: age/guardian workflow, redaction, reporting, moderation and a takedown process. |
| Low bandwidth and offline capture | Community contributors may have unstable connectivity and costly data. | Bundled media for the interface; next: resumable uploads, compression, offline draft queues and assisted capture. |
| Long-term preservation | A working app is not yet a durable archive. | SQLite, local media, JSON export and backup guidance; next: checksums, preservation formats, redundant storage and restoration drills. |
| Trust and provenance | An attractive AI biography can sound more certain than its source. | Source, translation and drafts separate; audit events and human review; next: version history, timestamps, per-claim source links and named reviewers. |
| Discoverability without extraction | Increased visibility should benefit creators and communities. | Creator attribution; next: creator contact preferences, benefit sharing, community partnerships and multilingual search. |
| Operating costs | Video, AI retries and long recordings can become expensive. | 24 MB upload cap and AI opt-in; next: per-account budgets, duration limits, jobs, quotas and cost reporting. |

These are product design considerations, not a legal determination. Seek appropriate local expertise for applicable privacy and cultural/IP requirements before launch.

## Requirements coverage

| Brief | Delivered | Remaining |
| --- | --- | --- |
| Mobile-friendly responsive app | Responsive React UI, accessible labels/focus, light/dark mode and reduced motion | Device testing with actual contributors, language-localised interface, formal accessibility audit |
| Username and password creation | Django registration/login/logout, hashed passwords, CSRF and password validation | Recovery, email verification, brute-force throttling, MFA and administrative roles |
| Upload video, pictures and audio | One file per story, format/signature checks, 24 MB cap, private serving, audio recording | Multiple files/galleries, resumable uploads, media scanning, transcoding and subtitle tracks |
| Identify and translate uploaded content | Optional OpenAI transcription or image text extraction, then source-language identification and English translation | Live multilingual quality evaluation; linguistic detection needs words, not an image's appearance; audio description of silent video is not implemented |
| Named artists' bios and pictures | All four profiles with linked sources and attribution | Artist approvals and permission for public reuse of the two contemporary artist images |
| Story Atlas | Clickable Natural Earth country map, search and language/category/region filters | Province polygons, nearby creator geospatial queries, island states missing from low-resolution geometry, disputed-boundary policy |
| Unsung Voices | Biography, article, timeline, context, tags and documentary/podcast written outlines from source notes | Creator profile entities, richer interview workflows, rendered media, educational collections |
| Publishing / export | Publish, withdraw, JSON record export, copied story text and browser PDF of published stories | Hosted links, portfolio aggregation, preservation packages with media and native PDF templates |
| Landing page | Hero, mission, four steps, creators, Unsung Voices, trust section, vision and CTA | Real impact metrics and quotes after pilot evidence exists; project contact/social accounts once supplied |

No invented impact statistics, artist quotations, endorsements or AI-generated biographies are presented as verified evidence. Source biographies are short editorial summaries. Unknown artist language information is explicitly not inferred.

## Suggested pilot

Start with a small partner community and one art form. Co-design permissions and interview questions; agree who reviews the source and English translation; record a handful of consented stories; test finding, withdrawing, exporting and restoring them. Track consent completeness, reviewer corrections, creator satisfaction and successful recovery from backup before expanding.

## Validation at delivery

- TypeScript check and production frontend build pass.
- Eight backend integration tests cover registration/password hashing/CSRF, permission isolation, valid and invalid image upload, publication and withdrawal, review invalidation, cultural restrictions, missing AI key, mocked AI output and export audit events.
- Browser checks cover the landing page, editorial cards, country map/filter behaviour and signed-out studio.
- A live OpenAI request and microphone/video capture have not been exercised; those need a configured key, FFmpeg where relevant and device permissions.
- Localhost launcher and bundled static assets are smoke-tested separately from Vite development preview.
