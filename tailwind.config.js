module.exports = {
  content: [
    './*.html',
    './services/**/*.html',
    './locations/**/*.html',
    './blog/**/*.html',
    './helpful-tips/**/*.html',
    './tools/*.py',
    './js/blog-search.js',
    './js/box-shop.js',
    ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        md: '2rem',
        lg: '3rem',
      }
    },  
    fontFamily: {
      'body': ['Barlow', 'sans-serif']
    },
    extend: {
      fontSize: {
        'xs': '.75rem',
        'sm': '.875rem',
        'tiny': '.875rem',
        'base': '1rem',
        'lg': '1.125rem',
        'xl': '1.25rem',
        '2xl': '1.5rem',
        '3xl': '1.875rem',
        '4xl': '2.25rem',
        '5xl': '3rem',
        '6xl': '4rem',
        '7xl': '5rem',
      },
      colors: {
        // Orwell Removals & Storage palette (navy + royal blue + tan, from logo + brand photos).
        // Token NAMES are kept identical to the Wolves base so the engine/CSS need no class renames;
        // only the VALUES change. Roles noted inline.
        transparent: 'transparent',
        current: 'currentColor',
        'white': '#ffffff',
        'black': '#1F2933',     // body text + headings (near-black slate)
        'blue': '#396299',      // links / primary brand royal
        'darkgrey': '#2E4D6B',  // dark navy-slate: card hover, top bar, deep sections
        'lightgrey': '#F4F7FB', // light cool section background
        'beige': '#E7EEF6',     // pale blue tint: alternating cards/sections + header
        'green': '#2D6FC9',     // CTA blue: primary buttons + ticks
        'darkgreen': '#254063', // navy: "Call Us" FAB + deepest brand
        'orange': '#C9A87C',    // tan accent (logo outline): underline bars, hovers
        'star': '#F6BB06',      // review stars (gold)
        'overlay': '#0B1A2B',   // navy hero overlay
        'border': '#E7E7E7',
      },
      listStyleImage: {
        checkmark: 'url("/wp-content/themes/wolvesremovals/img/check.svg")',
      },
    }
  },
  safelist: [
    'stf__parent',
    'stf__block',
    'stf__wrapper',
    '--portrait',
    'guide-page',
    'guide-flipbook',
    'lg:col-span-1',
    'lg:col-span-2',
    'lg:col-span-3',
    'lg:col-span-4',
    'lg:col-span-5',
    'lg:col-span-6',
    'lg:col-span-7',
    'lg:col-span-8',
    'lg:col-span-9',
    'lg:col-span-10',
    'lg:col-span-11',
    'lg:col-span-12',
    'md:col-span-1',
    'md:col-span-2',
    'md:col-span-3',
    'md:col-span-4',
    'md:col-span-5',
    'md:col-span-6',
    'md:col-span-7',
    'md:col-span-8',
    'md:col-span-9',
    'md:col-span-10',
    'md:col-span-11',
    'md:col-span-12',
    'pb-0',
    'pb-8',
    'pb-16',
    'pb-24',
    'pt-0',
    'pt-8',
    'pt-16',
    'pt-24',
    'pt-7',
    'lg:columns-2',
    'lg:columns-3',
    'lg:columns-4',
    'leading-loose',
    'lg:text-center',
    'lg:text-right',
    'lg:text-left',
    'bg-lightgrey',
  ],
  plugins: [],
}