export interface DestinationData {
  slug: string;
  name: string;
  tagline: string;
  description: string;
  facts: {
    gravity: string;
    distanceFromEarth: string;
    typicalTransitTime: string;
    surfaceTemp: string;
    moons: string;
    atmosphere: string;
  };
  hazards: string[];
  gallery: {
    alt: string;
    description: string;
    colorClass: string;
  }[];
  accentColor: string;
  bgAccent: string;
  borderAccent: string;
}

const destinations: DestinationData[] = [
  {
    slug: 'earth',
    name: 'Earth',
    tagline: 'The cradle of humanity — and the perfect place to return to.',
    description:
      'Earth remains the most habitable world in the known solar system, with a breathable nitrogen-oxygen atmosphere, liquid water oceans, and a magnetic field that shields surface life from solar radiation. Whether you\'re departing or arriving, orbital approach offers unrivalled views of swirling cloud systems and turquoise seas.',
    facts: {
      gravity: '9.81 m/s²',
      distanceFromEarth: '0 km',
      typicalTransitTime: 'Home port',
      surfaceTemp: '-89 °C to +57 °C',
      moons: '1 (Luna)',
      atmosphere: 'Nitrogen 78 %, Oxygen 21 %',
    },
    hazards: [
      'Dense air traffic in low-Earth orbit — strict approach corridors enforced',
      'Electromagnetic interference from surface networks may disrupt navigation',
      'Weather re-entry delays are common at equatorial spaceports',
      'Customs and biosecurity screening required for all interplanetary arrivals',
    ],
    gallery: [
      { alt: 'Blue Marble view', description: 'Blue Marble — Atlantic from orbit', colorClass: 'bg-blue-500/20' },
      { alt: 'Coastal landing strip', description: 'Cape Canaveral approach corridor', colorClass: 'bg-cyan-500/20' },
      { alt: 'Night lights', description: 'City grid illumination, night side', colorClass: 'bg-indigo-500/20' },
    ],
    accentColor: 'text-space-blue',
    bgAccent: 'bg-blue-500/10',
    borderAccent: 'border-blue-500/30',
  },
  {
    slug: 'mars',
    name: 'Mars',
    tagline: 'Rust-red horizons and the promise of a second home.',
    description:
      'Mars is humanity\'s boldest frontier — a terrestrial planet with a thin carbon dioxide atmosphere, polar ice caps, and the largest volcano in the solar system. Olympus Base offers pressurised habitats, rover excursions across Valles Marineris, and spectacular iron-oxide sunsets.',
    facts: {
      gravity: '3.72 m/s²',
      distanceFromEarth: '~225 million km (avg)',
      typicalTransitTime: '8 h',
      surfaceTemp: '-125 °C to +20 °C',
      moons: '2 (Phobos, Deimos)',
      atmosphere: 'CO₂ 95 %, thin — unsuitable for breathing',
    },
    hazards: [
      'Dust storms can ground all surface operations for weeks',
      'EVA suit required at all times outside pressurised zones',
      'Radiation exposure ~2× Earth levels — shielding mandatory',
      'Gravity adjustment syndrome affects most travellers for 48–72 h',
      'Perchlorate soil contamination — never remove gloves outdoors',
    ],
    gallery: [
      { alt: 'Olympus Mons', description: 'Olympus Mons caldera at dawn', colorClass: 'bg-orange-600/20' },
      { alt: 'Valles Marineris', description: 'Valles Marineris canyon system', colorClass: 'bg-red-700/20' },
      { alt: 'Polar ice cap', description: 'North polar CO₂ ice cap, summer', colorClass: 'bg-rose-300/20' },
    ],
    accentColor: 'text-solar-orange',
    bgAccent: 'bg-solar-orange/10',
    borderAccent: 'border-solar-orange/30',
  },
  {
    slug: 'moon',
    name: 'Moon',
    tagline: 'Humanity\'s first step — now a bustling gateway world.',
    description:
      'Just 384,000 km from Earth, the Moon is the solar system\'s most accessible off-world destination. Lunar Gateway Station and Artemis Base Camp provide modern amenities, while the stark regolith plains and Earth-rise views make for an unforgettable experience.',
    facts: {
      gravity: '1.62 m/s²',
      distanceFromEarth: '~384,000 km',
      typicalTransitTime: '3 h',
      surfaceTemp: '-173 °C to +127 °C',
      moons: 'N/A — the Moon itself',
      atmosphere: 'Virtually none (exosphere only)',
    },
    hazards: [
      'No atmosphere — space suit required outside at all times',
      'Micro-meteorite impacts are a persistent risk in the regolith zone',
      'Temperature swings exceed 300 °C between day and night',
      'Abrasive lunar dust can damage seals and optical surfaces',
    ],
    gallery: [
      { alt: 'Earthrise', description: 'Earthrise over the Sea of Tranquility', colorClass: 'bg-gray-400/20' },
      { alt: 'Artemis Base', description: 'Artemis Base Camp habitat cluster', colorClass: 'bg-slate-400/20' },
      { alt: 'Crater rim', description: 'Shackleton crater rim, south pole', colorClass: 'bg-zinc-400/20' },
    ],
    accentColor: 'text-star-white',
    bgAccent: 'bg-white/10',
    borderAccent: 'border-white/30',
  },
  {
    slug: 'venus',
    name: 'Venus',
    tagline: 'Hellscape below, paradise above the clouds.',
    description:
      'Venus is the solar system\'s most extreme planet — crushing atmospheric pressure, sulphuric acid clouds, and surface temperatures hot enough to melt lead. Galaxium\'s Cloud City habitats float at 50 km altitude where temperature and pressure are surprisingly Earth-like, offering surreal amber skies and lightning storms below.',
    facts: {
      gravity: '8.87 m/s²',
      distanceFromEarth: '~38 million km (closest)',
      typicalTransitTime: '6 h',
      surfaceTemp: '~465 °C (surface) / 0–30 °C (cloud layer)',
      moons: '0',
      atmosphere: 'CO₂ 96 %, H₂SO₄ clouds — lethal at surface',
    },
    hazards: [
      'Surface descent is strictly prohibited — habitat stays airborne',
      'Sulphuric acid rain can dissolve exposed equipment within hours',
      'Atmospheric turbulence rating 9/10 — expect a rough arrival',
      'Pressurisation failure evacuation time: under 90 seconds',
      'All exterior maintenance requires level-4 acid-resistant suits',
    ],
    gallery: [
      { alt: 'Cloud City', description: 'Aerostat Cloud City at 50 km altitude', colorClass: 'bg-yellow-500/20' },
      { alt: 'Lightning storm', description: 'Sulphuric acid lightning storms below', colorClass: 'bg-amber-600/20' },
      { alt: 'Solar panels', description: 'Solar array wings above the cloud deck', colorClass: 'bg-yellow-300/20' },
    ],
    accentColor: 'text-solar-orange',
    bgAccent: 'bg-yellow-500/10',
    borderAccent: 'border-yellow-500/30',
  },
  {
    slug: 'jupiter',
    name: 'Jupiter',
    tagline: 'King of planets — come for the storms, stay for the scale.',
    description:
      'Jupiter\'s swirling bands of ammonia and hydrogen stretch across a disc 11 times wider than Earth. Galileo Station orbits above the Great Red Spot, offering research suites, observation decks, and the most dramatic sky-scape in the solar system. Not for the faint-hearted.',
    facts: {
      gravity: '24.79 m/s² (at cloud tops)',
      distanceFromEarth: '~628 million km (avg)',
      typicalTransitTime: '18 h',
      surfaceTemp: '-108 °C (cloud tops)',
      moons: '95 known (Io, Europa, Ganymede, Callisto — largest)',
      atmosphere: 'H₂ 90 %, He 10 % — immense pressure at depth',
    },
    hazards: [
      'Radiation belts around Jupiter are among the most intense in the solar system',
      'Magnetic field disrupts electronics — shielded hull required',
      'No solid surface — descent below cloud tops is a one-way journey',
      'Orbital insertion requires precise timing to avoid moon conjunctions',
      'Gravitational tidal stresses can cause hull fatigue on long stays',
    ],
    gallery: [
      { alt: 'Great Red Spot', description: 'Great Red Spot storm system, 350-year duration', colorClass: 'bg-orange-400/20' },
      { alt: 'Galileo Station', description: 'Galileo Station orbital platform', colorClass: 'bg-amber-700/20' },
      { alt: 'Moon transit', description: 'Io transit shadow across the equatorial band', colorClass: 'bg-red-400/20' },
    ],
    accentColor: 'text-solar-orange',
    bgAccent: 'bg-orange-500/10',
    borderAccent: 'border-orange-500/30',
  },
  {
    slug: 'europa',
    name: 'Europa',
    tagline: 'Beneath the ice: the best chance of alien life in our solar system.',
    description:
      'Europa\'s fractured ice shell hides a vast subsurface ocean that may harbour microbial life. Research Station Icebreaker sits at the surface, while deep-drilling missions descend toward the water below. Every visit contributes to one of the most exciting scientific endeavours in human history.',
    facts: {
      gravity: '1.315 m/s²',
      distanceFromEarth: '~628 million km (avg)',
      typicalTransitTime: '19 h',
      surfaceTemp: '-160 °C to -220 °C',
      moons: 'Moon of Jupiter',
      atmosphere: 'Thin oxygen exosphere — not breathable',
    },
    hazards: [
      'Jupiter\'s radiation at Europa\'s orbit is intense — exterior exposure is time-limited to 1 hour',
      'Ice crust seismic "ice-quakes" can crack landing pad anchorings',
      'Cryoventing plumes erupt unpredictably — avoid surface EVA near fracture lines',
      'All samples require level-5 biosafety protocols — no surface material leaves containment',
    ],
    gallery: [
      { alt: 'Ice fractures', description: 'Linea fracture network from orbit', colorClass: 'bg-cyan-400/20' },
      { alt: 'Icebreaker Station', description: 'Icebreaker Station drill array, surface', colorClass: 'bg-teal-400/20' },
      { alt: 'Jupiter in sky', description: 'Jupiter rising over Europa\'s ice plain', colorClass: 'bg-blue-400/20' },
    ],
    accentColor: 'text-alien-green',
    bgAccent: 'bg-alien-green/10',
    borderAccent: 'border-alien-green/30',
  },
  {
    slug: 'pluto',
    name: 'Pluto',
    tagline: 'The edge of the known — for travellers who want more.',
    description:
      'Pluto sits at the outer frontier of our solar system, a nitrogen-ice world with heart-shaped plains, soaring methane mountains, and a hazy blue atmosphere. Sputnik Base is the most remote inhabited outpost in human history, and arrival is a rite of passage for serious space explorers.',
    facts: {
      gravity: '0.62 m/s²',
      distanceFromEarth: '~5.9 billion km (avg)',
      typicalTransitTime: '36 h',
      surfaceTemp: '-233 °C to -223 °C',
      moons: '5 (Charon, Styx, Nix, Kerberos, Hydra)',
      atmosphere: 'N₂, CH₄, CO — thin and seasonal',
    },
    hazards: [
      'Extreme cold requires next-generation cryo-insulated EVA suits',
      'Low gravity increases fall risk — standard locomotion training required',
      'Communication lag to Earth exceeds 4 hours — emergency response is self-reliant',
      'Nitrogen geysers can emerge without warning near Tombaugh Regio',
      'Methane frost on landing pads creates slippery surfaces — approach speed limits enforced',
    ],
    gallery: [
      { alt: 'Tombaugh Regio', description: 'Tombaugh Regio nitrogen ice plains ("The Heart")', colorClass: 'bg-purple-400/20' },
      { alt: 'Charon from surface', description: 'Charon looming over Sputnik Base', colorClass: 'bg-violet-500/20' },
      { alt: 'Blue haze atmosphere', description: 'Blue haze layers in Pluto\'s thin atmosphere', colorClass: 'bg-indigo-400/20' },
    ],
    accentColor: 'text-cosmic-purple',
    bgAccent: 'bg-cosmic-purple/10',
    borderAccent: 'border-cosmic-purple/30',
  },
];

// Lookup by URL slug (case-insensitive)
export const getDestinationBySlug = (slug: string): DestinationData | null =>
  destinations.find((d) => d.slug === slug.toLowerCase()) ?? null;

// Lookup by display name (used to linkify destination names in FlightCard)
export const getDestinationByName = (name: string): DestinationData | null =>
  destinations.find((d) => d.name.toLowerCase() === name.toLowerCase()) ?? null;

// All destinations for the homepage grid
export const ALL_DESTINATIONS: ReadonlyArray<DestinationData> = destinations;

// Made with Bob
