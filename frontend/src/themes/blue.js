/**
 * Blue theme — Malaysia Airlines client
 * Values are HSL components (no hsl() wrapper) to match Tailwind's hsl(var(--x)) pattern.
 * #004B87 ≈ hsl(207,100%,26%)  #0066CC ≈ hsl(210,100%,40%)  #003580 ≈ hsl(215,100%,25%)
 * #D4AF37 ≈ hsl(46,62%,52%)   #F5A623 ≈ hsl(37,90%,55%)
 * #1A1A1A ≈ hsl(0,0%,10%)     #E0E0E0 ≈ hsl(0,0%,88%)
 */
const blue = {
  '--primary':            '207 100% 26%',   /* #004B87 — MAS signature blue */
  '--primary-dark':       '215 100% 25%',   /* #003580 — deep blue for header gradient */
  '--primary-light':      '210 100% 40%',   /* #0066CC — hover/focus states */
  '--primary-foreground': '0 0% 100%',
  '--secondary':          '46 62% 52%',     /* #D4AF37 — gold accent */
  '--secondary-hover':    '37 90% 55%',     /* #F5A623 — warm gold hover */
  '--secondary-foreground': '0 0% 10%',
  '--background':         '0 0% 100%',
  '--foreground':         '0 0% 10%',       /* #1A1A1A — neutral dark gray (was dark navy) */
  '--card':               '0 0% 100%',
  '--card-foreground':    '0 0% 10%',       /* #1A1A1A — neutral dark gray (was dark navy) */
  '--muted':              '0 0% 96%',       /* #F5F5F5 — light gray background */
  '--muted-foreground':   '0 0% 20%',       /* #333333 — secondary text */
  '--accent':             '210 50% 95%',
  '--accent-foreground':  '207 100% 26%',
  '--destructive':        '0 84% 60%',      /* ≈ #E74C3C */
  '--destructive-foreground': '0 0% 100%',
  '--border':             '0 0% 88%',       /* #E0E0E0 — neutral gray border (was blue-tinted) */
  '--input':              '0 0% 88%',
  '--ring':               '207 100% 26%',
};

export default blue;
