/* Original examples; never represented as user-authored work. */
globalThis.WORKBENCH_TEMPLATES=[
{id:'flow',name:'From idea to something real',type:'Flowchart',group:'Processes',description:'A maker-friendly process, complete with a useful feedback loop.',source:`flowchart TD
    accTitle: From idea to something real
    accDescr: An idea moves through sketching, making, testing, and sharing. Testing can lead back to making.

    IDEA(["A small, good idea"]) --> SKETCH["Sketch the possibility"]
    SKETCH --> MAKE["Make a first version"]
    MAKE --> TEST{"Does it do the job?"}
    TEST -->|Not quite| LEARN["Learn one useful thing"]
    LEARN --> MAKE
    TEST -->|Good enough| SHARE(["Share it with the world"])

    classDef seed fill:#ddefbc,stroke:#637b3b,color:#213418
    classDef action fill:#e5eafa,stroke:#8292b8,color:#293959
    classDef question fill:#ffe9bc,stroke:#b48e46,color:#604810
    class IDEA,SHARE seed
    class SKETCH,MAKE,LEARN action
    class TEST question`},
{id:'sequence',name:'A conversation between systems',type:'Sequence',group:'Software',description:'Requests, responses, and an alternative outcome.',source:`sequenceDiagram
    autonumber
    actor Maker
    participant App as Workbench
    participant Store as Local storage
    Maker->>App: Change a diagram
    App->>App: Validate source
    alt Valid syntax
        App-->>Maker: Show updated preview
    else Needs attention
        App-->>Maker: Keep last valid preview
    end
    App->>Store: Save editable source
    Store-->>App: Saved on this device`},
{id:'state',name:'The life of a repair',type:'State',group:'Processes',description:'States, transitions, and a composite workflow.',source:`stateDiagram-v2
    [*] --> Received
    Received --> Diagnosing: Open the case
    Diagnosing --> Repairing: Fault found
    Diagnosing --> Waiting: Need a part
    Waiting --> Repairing: Part arrives
    Repairing --> Testing
    Testing --> Repairing: Try again
    Testing --> Returned: Works safely
    Returned --> [*]`},
{id:'class',name:'Objects on the workbench',type:'Class',group:'Software',description:'Classes, methods, inheritance, and composition.',source:`classDiagram
    class Instrument {
        +String name
        +String version
        +open()
        +export()
    }
    class Diagram {
        +String source
        +validate()
        +render()
    }
    class Snapshot {
        +Date created
        +String source
        +restore()
    }
    Instrument "1" *-- "many" Diagram
    Diagram "1" *-- "many" Snapshot`},
{id:'er',name:'Parts, bins, and projects',type:'Entity relationship',group:'Software',description:'A small inventory schema with relationships.',source:`erDiagram
    BIN ||--o{ PART : contains
    PROJECT ||--o{ ALLOCATION : needs
    PART ||--o{ ALLOCATION : supplies
    BIN {
        string id PK
        string label
        string location
    }
    PART {
        string id PK
        string name
        int quantity
    }
    PROJECT {
        string id PK
        string title
    }
    ALLOCATION {
        string project_id FK
        string part_id FK
        int quantity
    }`},
{id:'gantt',name:'A four-week prototype',type:'Gantt',group:'Planning',description:'Dependencies, milestones, and overlapping work.',source:`gantt
    title A four-week prototype
    dateFormat YYYY-MM-DD
    axisFormat %b %d
    excludes weekends
    section Discover
    Understand the need :done, need, 2026-09-21, 3d
    Sketch alternatives :sketch, after need, 2d
    section Make
    Electronics :electronics, after sketch, 5d
    Enclosure :enclosure, after sketch, 5d
    Firmware :firmware, after electronics, 4d
    section Learn
    Test and refine :test, after firmware, 4d
    Share the result :milestone, after test, 0d`},
{id:'mindmap',name:'Ways of making',type:'Mindmap',group:'Ideas',description:'Organize a central idea into useful branches.',source:`mindmap
  root((Making))
    Learn
      Ask a question
      Try a small experiment
      Share a discovery
    Repair
      Understand the fault
      Keep something useful
    Create
      Sketch
      Build
      Play
    Together
      Teach a skill
      Borrow a tool
      Welcome someone new`},
{id:'timeline',name:'From sketch to shared knowledge',type:'Timeline',group:'Planning',description:'A timeline with phases and related events.',source:`timeline
    title From sketch to shared knowledge
    section Explore
        Week 1 : Listen : Sketch : Ask questions
    section Build
        Week 2 : Make the first version
        Week 3 : Test : Improve : Document
    section Share
        Week 4 : Demonstrate : Teach : Publish notes`},
{id:'journey',name:'A first visit to the workshop',type:'Journey',group:'People',description:'Experience scores across a human-centered journey.',source:`journey
    title A first visit to the workshop
    section Arriving
      Find the door: 3: Visitor
      Get a warm welcome: 5: Visitor, Host
    section Making
      Pick a small project: 4: Visitor, Host
      Try something unfamiliar: 3: Visitor
      Make it work: 5: Visitor, Host
    section Leaving
      Share what happened: 5: Visitor, Host`},
{id:'pie',name:'A day at the workbench',type:'Pie',group:'Data',description:'A simple part-to-whole breakdown.',source:`pie showData
    title A day at the workbench
    "Making" : 45
    "Learning" : 20
    "Repairing" : 20
    "Sharing" : 15`},
{id:'quadrant',name:'Deciding what to make next',type:'Quadrant',group:'Planning',description:'Compare opportunities on two dimensions.',source:`quadrantChart
    title What should we make next?
    x-axis Small effort --> Large effort
    y-axis Modest usefulness --> High usefulness
    quadrant-1 Plan deliberately
    quadrant-2 Start here
    quadrant-3 A small experiment
    quadrant-4 Reconsider scope
    Parts labeler: [0.25, 0.8]
    Community tool library: [0.8, 0.85]
    Desk ornament: [0.2, 0.25]
    Everything app: [0.9, 0.3]`},
{id:'git',name:'A release without surprises',type:'Git graph',group:'Software',description:'Branches, commits, and a release merge.',source:`gitGraph
    commit id: "Starting point"
    branch feature
    checkout feature
    commit id: "First pass"
    commit id: "Add tests"
    checkout main
    commit id: "Documentation"
    merge feature
    commit id: "Release" tag: "v1.0"`},
{id:'requirement',name:'A requirement with evidence',type:'Requirement',group:'Engineering',description:'Connect a requirement to a verification element.',source:`requirementDiagram
    requirement local_first {
        id: R1
        text: Works without an internet connection
        risk: medium
        verifymethod: test
    }
    element offline_test {
        type: "test"
        docref: "Test record 01"
    }
    offline_test - verifies -> local_first`},
{id:'c4',name:'A system in context',type:'C4 context',group:'Software',description:'People, your system, and an external system.',source:`C4Context
    title Workshop booking context
    Person(maker, "Maker", "Finds and joins a workshop")
    System(booking, "Booking system", "Organizes workshop places")
    System_Ext(email, "Email service", "Delivers confirmations")
    Rel(maker, booking, "Books a place")
    Rel(booking, email, "Requests confirmation")`},
{id:'sankey',name:'Where the material goes',type:'Sankey',group:'Data',description:'Flows between sources and destinations.',source:`sankey-beta
    Salvaged,Repaired,30
    Salvaged,Reused,45
    Salvaged,Recycled,25
    Repaired,Community,30
    Reused,New projects,45
    Recycled,Materials recovery,25`},
{id:'xy',name:'Small improvements add up',type:'XY chart',group:'Data',description:'Bars and a line on a shared chart.',source:`xychart-beta
    title "Projects completed"
    x-axis [Jan, Feb, Mar, Apr, May, Jun]
    y-axis "Projects" 0 --> 20
    bar [4, 7, 6, 11, 14, 17]
    line [3, 5, 7, 9, 12, 15]`},
{id:'block',name:'A compact system layout',type:'Block',group:'Engineering',description:'Use a grid to communicate a system layout.',source:`block-beta
    columns 3
    A["Input"] B["Process"] C["Output"]
    D["Power"]:3
    A --> B
    B --> C
    D --> B`},
{id:'packet',name:'A tiny message protocol',type:'Packet',group:'Engineering',description:'A bit-level view of a simple packet.',source:`packet-beta
    title Tiny message protocol
    0-7: "Version"
    8-15: "Type"
    16-31: "Payload length"
    32-63: "Sequence number"
    64-95: "Checksum"`},
{id:'architecture',name:'A small local service',type:'Architecture',group:'Software',description:'Services, a database, and a connection.',source:`architecture-beta
    group local(cloud)[Local network]
    service app(server)[Workbench] in local
    service data(database)[Storage] in local
    app:R -- L:data`},
{id:'kanban',name:'Keep the work moving',type:'Kanban',group:'Planning',description:'A lightweight workflow, expressed as a diagram.',source:`kanban
    backlog[Ideas]
        idea1[Make a parts labeler]
        idea2[Repair a desk lamp]
    doing[In progress]
        task1[Sketch the enclosure]
    done[Shared]
        done1[Publish the wiring notes]`},
{id:'radar',name:'Two prototype directions',type:'Radar',group:'Data',description:'Compare illustrative scores across five dimensions.',source:`radar-beta
    title Prototype comparison
    axis a["Clarity"], b["Repairability"], c["Simplicity"], d["Portability"], e["Accessibility"]
    curve first["First idea"]{3, 4, 5, 2, 3}
    curve second["Revised idea"]{4, 5, 4, 4, 5}
    max 5
    min 0
    showLegend true`},
{id:'treemap',name:'An inventory at a glance',type:'Treemap',group:'Data',description:'Nested categories sized by illustrative quantities.',source:`treemap-beta
    "Parts"
        "Electronics"
            "Resistors": 120
            "Sensors": 25
            "Connectors": 60
        "Hardware"
            "Fasteners": 90
            "Brackets": 20`},
{id:'subgraph',name:'An offline-first instrument',type:'Flowchart',group:'Software',description:'A left-to-right architecture with grouped responsibilities.',source:`flowchart LR
    subgraph DEVICE["On your device"]
        EDIT["Edit source"] --> VALIDATE["Validate"]
        VALIDATE --> PREVIEW["Render preview"]
        EDIT --> SAVE[("Local workspace")]
    end
    SAVE --> JSON["Portable JSON backup"]
    PREVIEW --> SVG["SVG or PNG"]
    PREVIEW --> REPORT["Print-ready report"]`},
{id:'blank',name:'A clean sheet',type:'Flowchart',group:'Essentials',description:'Just two nodes. The next idea is yours.',source:`flowchart TD
    A["Start here"] --> B["Make something clear"]`}
];
