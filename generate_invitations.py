#!/usr/bin/env python3
"""
generate_invitations.py
Generates personalized standalone wedding invitation pages for each guest / couple based on guests.json.
Features:
- Consolidates couples into single shared invitation links with party size = 2
- Gracefully redirects individual member links to their shared couple link
- Tailored hero date header (3 days, 2 days, or Saturday only)
- Tailored welcome letterhead ("have you both by our side" for couples)
- Displays only invited event days (Friday Ciampini, Saturday Vatican & Villa Aurelia, Sunday Hassler Brunch)
- RSVP form with prefilled names and attending count selector for couples
- Snappy parallel Google Sheets + email submission (sub-second response)
- Responsive lookbook modals and clean E&D monogram preloader
- Generates INVITATIONS.md, guests.csv, and guest-directory.html for 1-click link copying!
"""

import json
import os
import re
import unicodedata
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GUESTS_FILE = os.path.join(BASE_DIR, 'guests.json')
FAUSTO_TEMPLATE_FILE = os.path.join(BASE_DIR, 'fausto.html')

# 18 Couples explicitly specified by Elia & Daniel
COUPLES_CONFIG = [
    {
        'members': ['Luigi Rafaiani', 'Giulia Rafaiani'],
        'display_name': 'Luigi & Giulia Rafaiani',
        'greeting': 'Dear Luigi & Giulia,',
        'first_name': 'Luigi & Giulia',
        'slug': 'luigi-and-giulia',
        'side': 'Elia Innamorati',
        'group': 'Family Rafaiani',
        'friday_ciampini': False,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Maria Chiara Rafaiani', 'Fabrizio Sinisi'],
        'display_name': 'Maria Chiara Rafaiani & Fabrizio Sinisi',
        'greeting': 'Dear Maria Chiara & Fabrizio,',
        'first_name': 'Maria Chiara & Fabrizio',
        'slug': 'maria-chiara-and-fabrizio',
        'side': 'Elia Innamorati',
        'group': 'Family Rafaiani',
        'friday_ciampini': False,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Roberto Picardi', 'Gabriela Picardi', ' Roberto Picardi'],
        'display_name': 'Gabriela & Roberto Picardi',
        'greeting': 'Dear Gabriela & Roberto,',
        'first_name': 'Gabriela & Roberto',
        'slug': 'gabriela-and-roberto',
        'side': 'Elia Innamorati',
        'group': 'Family',
        'friday_ciampini': False,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Roberto Castellani', 'Rodi Castellani'],
        'display_name': 'Roberto & Rodi Castellani',
        'greeting': 'Dear Roberto & Rodi,',
        'first_name': 'Roberto & Rodi',
        'slug': 'roberto-and-rodi',
        'side': 'Elia Innamorati',
        'group': 'Family Castellani',
        'friday_ciampini': False,
        'saturday_wedding': True,
        'sunday_brunch': False,
        'party_size': 2
    },
    {
        'members': ['Giovanni Castellani', 'Eleonora Castellani'],
        'display_name': 'Giovanni & Eleonora Castellani',
        'greeting': 'Dear Giovanni & Eleonora,',
        'first_name': 'Giovanni & Eleonora',
        'slug': 'giovanni-and-eleonora',
        'side': 'Elia Innamorati',
        'group': 'Family Castellani',
        'friday_ciampini': False,
        'saturday_wedding': True,
        'sunday_brunch': False,
        'party_size': 2
    },
    {
        'members': ['Elena Selicato', 'Sabino Selicato'],
        'display_name': 'Elena & Sabino Selicato',
        'greeting': 'Dear Elena & Sabino,',
        'first_name': 'Elena & Sabino',
        'slug': 'elena-and-sabino',
        'side': 'Elia Innamorati',
        'group': 'Family Selicato',
        'friday_ciampini': False,
        'saturday_wedding': True,
        'sunday_brunch': False,
        'party_size': 2
    },
    {
        'members': ['Akemy Ciccia', 'Miguel Angel Ciccia Ayllon'],
        'display_name': 'Akemy & Miguel Angel Ciccia',
        'greeting': 'Dear Akemy & Miguel Angel,',
        'first_name': 'Akemy & Miguel Angel',
        'slug': 'akemy-and-miguel',
        'side': 'Elia Innamorati',
        'group': 'Family Ciccia',
        'friday_ciampini': False,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Paola Ciccia Ayllon', "Paola's Husband", 'Denis'],
        'display_name': 'Paola Ciccia & Denis',
        'greeting': 'Dear Paola & Denis,',
        'first_name': 'Paola & Denis',
        'slug': 'paola-and-denis',
        'side': 'Elia Innamorati',
        'group': 'Family Ciccia',
        'friday_ciampini': False,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Filip Schelfhout', 'Adriana Leskiv'],
        'display_name': 'Filip Schelfhout & Adriana Leskiv',
        'greeting': 'Dear Filip & Adriana,',
        'first_name': 'Filip & Adriana',
        'slug': 'filip-and-adriana',
        'side': 'Daniel Meister',
        'group': 'Friends',
        'friday_ciampini': True,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Olena Gillian', 'Eric Gillian'],
        'display_name': 'Olena & Eric Gillian',
        'greeting': 'Dear Olena & Eric,',
        'first_name': 'Olena & Eric',
        'slug': 'olena-and-eric',
        'side': 'Daniel Meister',
        'group': 'Family Gillian',
        'friday_ciampini': True,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Elias Stassinopoulos', 'Marion', 'Marion '],
        'display_name': 'Elias Stassinopoulos & Marion',
        'greeting': 'Dear Elias & Marion,',
        'first_name': 'Elias & Marion',
        'slug': 'elias-and-marion',
        'side': 'Daniel Meister',
        'group': 'Friends',
        'friday_ciampini': True,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Michelle Blochlinger', 'Johannes Blochlinger'],
        'display_name': 'Michelle & Johannes Blochlinger',
        'greeting': 'Dear Michelle & Johannes,',
        'first_name': 'Michelle & Johannes',
        'slug': 'michelle-and-johannes',
        'side': 'Daniel Meister',
        'group': 'Friends',
        'friday_ciampini': True,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Nick Moore', 'Claude Moore', 'Claude Moore ', 'Claudia Moore'],
        'display_name': 'Nick & Claudia Moore',
        'greeting': 'Dear Nick & Claudia,',
        'first_name': 'Nick & Claudia',
        'slug': 'nick-and-claudia',
        'side': 'Daniel Meister',
        'group': 'Friends',
        'friday_ciampini': True,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Franz Grüter', 'Luzia Grüter'],
        'display_name': 'Luzia & Franz Grüter',
        'greeting': 'Dear Luzia & Franz,',
        'first_name': 'Luzia & Franz',
        'slug': 'luzia-and-franz',
        'side': 'Daniel Meister',
        'group': 'Family',
        'friday_ciampini': True,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Ines Franke', 'Nayam de Groot'],
        'display_name': 'Ines Franke & Nayam de Groot',
        'greeting': 'Dear Ines & Nayam,',
        'first_name': 'Ines & Nayam',
        'slug': 'ines-and-nayam',
        'side': 'Daniel Meister',
        'group': 'Friends',
        'friday_ciampini': True,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Lila Chertman Thompson', 'Adam Thompson'],
        'display_name': 'Lila & Adam Thompson',
        'greeting': 'Dear Lila & Adam,',
        'first_name': 'Lila & Adam',
        'slug': 'lila-and-adam',
        'side': 'Elia Innamorati',
        'group': 'Friends',
        'friday_ciampini': False,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Olga Padilla', 'Scott Scharg', 'Olga Padilla '],
        'display_name': 'Olga Padilla & Scott Scharg',
        'greeting': 'Dear Olga & Scott,',
        'first_name': 'Olga & Scott',
        'slug': 'olga-and-scott',
        'side': 'Elia Innamorati',
        'group': 'Friends',
        'friday_ciampini': False,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    },
    {
        'members': ['Franca Marnin', 'Arno Marnin'],
        'display_name': 'Franca & Arno Marnin',
        'greeting': 'Dear Franca & Arno,',
        'first_name': 'Franca & Arno',
        'slug': 'franca-and-arno',
        'side': 'Daniel Meister',
        'group': 'Friends',
        'friday_ciampini': True,
        'saturday_wedding': True,
        'sunday_brunch': True,
        'party_size': 2
    }
]

def slugify(text):
    text = text.replace('+ 1', 'plus-one').replace('+1', 'plus-one')
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).lower()
    return re.sub(r'[-\s]+', '-', text).strip('-')

def get_solo_greeting(name):
    name = name.strip()
    if 'Cardinal' in name:
        return 'Your Eminence,'
    if '+ 1' in name or '+1' in name:
        base = re.sub(r'\s*\+\s*1', '', name).strip()
        first = base.split()[0]
        return f'Dear {first} & Guest,'
    first = name.split()[0]
    return f'Dear {first},'

def get_solo_first_name(name):
    name = name.strip()
    if 'Cardinal' in name:
        return 'Your Eminence'
    if '+ 1' in name or '+1' in name:
        base = re.sub(r'\s*\+\s*1', '', name).strip()
        return base.split()[0] + ' & Guest'
    return name.split()[0]

def main():
    with open(GUESTS_FILE, 'r', encoding='utf-8') as f:
        guests = json.load(f)

    # 1. Clean up guest list strings & update Denis and Claudia
    for g in guests:
        g['name'] = g['name'].strip()
        if g['name'] == "Paola's Husband":
            g['name'] = "Denis"
            g['notes'] = "Husband of Paola Ciccia Ayllon"
        elif g['name'] == "Claude Moore":
            g['name'] = "Claudia Moore"

    # Map members to their couples
    couple_member_map = {}
    for c in COUPLES_CONFIG:
        for member_name in c['members']:
            couple_member_map[member_name.strip().lower()] = c

    # Build Invitation Entities (18 couples + 40 solo = 58 invitations)
    invitations = []
    processed_couples = set()
    solo_guests = []

    for g in guests:
        name_lower = g['name'].lower()
        if name_lower in couple_member_map:
            c = couple_member_map[name_lower]
            c_slug = c['slug']
            if c_slug not in processed_couples:
                processed_couples.add(c_slug)
                # Find min order among members
                member_orders = [
                    x.get('order', 999) for x in guests 
                    if x['name'].strip().lower() in [m.lower() for m in c['members']]
                ]
                min_order = min(member_orders) if member_orders else 999
                invitations.append({
                    'is_couple': True,
                    'order': min_order,
                    'slug': c['slug'],
                    'name': c['display_name'],
                    'greeting': c['greeting'],
                    'first_name': c['first_name'],
                    'party_size': c['party_size'],
                    'side': c['side'],
                    'group': c['group'],
                    'friday_ciampini': c['friday_ciampini'],
                    'saturday_wedding': c['saturday_wedding'],
                    'sunday_brunch': c['sunday_brunch'],
                    'members': c['members']
                })
            # Also attach couple info to guest record for guests.json / guests.csv
            g['is_couple'] = True
            g['couple_slug'] = c['slug']
            g['party_size'] = 2
            g['invitation_slug'] = c['slug']
            g['invitation_url'] = f"https://innamorati-meister.com/{c['slug']}"
        else:
            # Solo guest
            slug = slugify(g['name'])
            g['slug'] = slug
            g['is_couple'] = False
            g['couple_slug'] = None
            g['party_size'] = 1
            g['invitation_slug'] = slug
            g['invitation_url'] = f"https://innamorati-meister.com/{slug}"
            invitations.append({
                'is_couple': False,
                'order': g.get('order', 999),
                'slug': slug,
                'name': g['name'],
                'greeting': get_solo_greeting(g['name']),
                'first_name': get_solo_first_name(g['name']),
                'party_size': 1,
                'side': g.get('side', '-'),
                'group': g.get('group', '-'),
                'friday_ciampini': bool(g.get('friday_ciampini', False)),
                'saturday_wedding': True,
                'sunday_brunch': bool(g.get('sunday_brunch', True)),
                'members': [g['name']]
            })

    # Sort invitations by order
    invitations.sort(key=lambda x: x['order'])

    # Save updated guests.json
    with open(GUESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(guests, f, indent=2, ensure_ascii=False)

    with open(FAUSTO_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()

    # Extract Day sections from fausto.html
    d1_match = re.search(r'(<!-- DAY 1: FRIDAY, APRIL 16 -->[\s\S]*?)(?=<!-- DAY 2: SATURDAY, APRIL 17 -->)', template)
    day1_section = d1_match.group(1) if d1_match else ''

    d2_match = re.search(r'(<!-- DAY 2: SATURDAY, APRIL 17 -->[\s\S]*?)(?=<!-- DAY 3: SUNDAY, APRIL 18 -->)', template)
    day2_section = d2_match.group(1) if d2_match else ''

    d3_match = re.search(r'(<!-- DAY 3: SUNDAY, APRIL 18 -->[\s\S]*?)(?=<!-- RSVP Section)', template)
    day3_section = d3_match.group(1) if d3_match else ''

    # Extract Event cards from RSVP section
    ev1_match = re.search(r'(<!-- Event 1 -->[\s\S]*?)(?=<!-- Event 2 -->)', template)
    event1_card = ev1_match.group(1) if ev1_match else ''

    ev2_match = re.search(r'(<!-- Event 2 -->[\s\S]*?)(?=<!-- Event 3 -->)', template)
    event2_card = ev2_match.group(1) if ev2_match else ''

    ev3_match = re.search(r'(<!-- Event 3 -->[\s\S]*?)(?=</div>\s*<div class="stationery-input-group)', template)
    event3_card = ev3_match.group(1) if ev3_match else ''

    # Extract base head/hero and footer
    head_hero_match = re.search(r'([\s\S]*?)(?=<!-- Personal Invitation Letterhead -->)', template)
    head_hero_base = head_hero_match.group(1) if head_hero_match else ''

    footer_match = re.search(r'(<!-- Attire Lookbook Modal -->[\s\S]*)', template)
    footer_base = footer_match.group(1) if footer_match else ''

    # Clean preloader: remove glowing halo and spinning ring for clean calligraphy
    head_hero_base = head_hero_base.replace('<div class="preloader-halo"></div>', '')
    head_hero_base = head_hero_base.replace('<div class="preloader-ring"></div>', '')

    # Add custom select style to head
    select_style = """
    select.stationery-line-input {
      cursor: pointer;
      -webkit-appearance: none;
      -moz-appearance: none;
      appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8' fill='none'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%23BFA175' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 0.75rem center;
      padding-right: 2rem;
    }
    select.stationery-line-input option {
      background: #FAF9F6;
      color: #1A1918;
      font-family: var(--font-sans);
      font-size: 0.95rem;
      padding: 0.5rem;
    }
  </style>"""
    head_hero_base = head_hero_base.replace('</style>', select_style)

    directory_entries = []

    for inv in invitations:
        name = inv['name']
        slug = inv['slug']
        is_couple = inv['is_couple']
        party_size = inv['party_size']

        has_fri = inv['friday_ciampini']
        has_sat = inv['saturday_wedding']
        has_sun = inv['sunday_brunch']

        greeting = inv['greeting']
        first_name = inv['first_name']

        pronoun_phrase = "have you both by our side" if is_couple else "have you by our side"

        # Dates & Location Header & Welcome Text
        if has_fri and has_sun:
            dates_header = "APRIL 16 · 17 · 18, 2027"
            meta_desc = "April 16 · 17 · 18, 2027 — Rome, Italy."
            welcome_text = (
                f"We are overjoyed to invite you to celebrate our wedding in Rome with us. "
                f"It is a true honour and immense joy to {pronoun_phrase} for the entire weekend &mdash; "
                f"from our welcome dinner overlooking the Eternal City, to our nuptial blessing in the Vatican, "
                f"our evening gala at Villa Aurelia, and our farewell rooftop brunch."
            )
        elif has_fri and not has_sun:
            dates_header = "APRIL 16 · 17, 2027"
            meta_desc = "April 16 · 17, 2027 — Rome, Italy."
            welcome_text = (
                f"We are overjoyed to invite you to celebrate our wedding in Rome with us. "
                f"It is a true honour and immense joy to {pronoun_phrase} &mdash; "
                f"from our welcome dinner overlooking the Eternal City, to our nuptial blessing in the Vatican "
                f"and our evening gala banquet at historic Villa Aurelia."
            )
        elif not has_fri and has_sun:
            dates_header = "APRIL 17 · 18, 2027"
            meta_desc = "April 17 · 18, 2027 — Rome, Italy."
            welcome_text = (
                f"We are overjoyed to invite you to celebrate our wedding in Rome with us. "
                f"It is a true honour and immense joy to {pronoun_phrase} &mdash; "
                f"from our nuptial blessing in the Choir Chapel of St. Peter's Basilica and evening gala at historic Villa Aurelia, "
                f"to our farewell rooftop brunch overlooking the Spanish Steps."
            )
        else: # Saturday only
            dates_header = "APRIL 17, 2027"
            meta_desc = "April 17, 2027 — Rome, Italy."
            welcome_text = (
                f"We are overjoyed to invite you to celebrate our wedding in Rome with us. "
                f"It is a true honour and immense joy to {pronoun_phrase} for our nuptial blessing in the "
                f"Choir Chapel of St. Peter's Basilica, followed by our evening celebratory gala dinner and dancing under the stars at historic Villa Aurelia."
            )

        # Build Head & Hero
        guest_head_hero = head_hero_base
        guest_head_hero = re.sub(r'<title>.*?</title>', f'<title>Elia & Daniel | Rome · Invitation for {name}</title>', guest_head_hero)
        guest_head_hero = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="Elia & Daniel | Invitation for {name}">', guest_head_hero)
        guest_head_hero = re.sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{meta_desc}">', guest_head_hero)
        guest_head_hero = re.sub(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="https://innamorati-meister.com/{slug}">', guest_head_hero)
        
        # Replace date header in hero
        guest_head_hero = re.sub(
            r'<div class="location-text">[\s\S]*?</div>',
            f'<div class="location-text">\n        {dates_header}\n      </div>',
            guest_head_hero
        )

        # Build Welcome Letterhead
        welcome_section = f"""    <!-- Personal Invitation Letterhead -->
    <section class="welcome-editorial" id="invitation">
      <h2 class="welcome-title reveal-item" style="--delay: 0.1s;">{greeting}</h2>
      <p class="welcome-text reveal-item" style="--delay: 0.25s;">
        {welcome_text}
      </p>
      <div class="editorial-divider reveal-item" style="--delay: 0.4s;"></div>
    </section>
"""

        # Build Days
        days_html = ""
        if has_fri:
            days_html += day1_section
        days_html += day2_section
        if has_sun:
            days_html += day3_section

        # Build RSVP Events
        rsvp_events_html = '<div class="stationery-event-list">\n'
        if has_fri:
            rsvp_events_html += event1_card
        rsvp_events_html += event2_card
        if has_sun:
            rsvp_events_html += event3_card
        rsvp_events_html += '        </div>\n'

        # Build RSVP Form (with party size dropdown for couples)
        if is_couple:
            pax_selector_html = """
        <div class="stationery-input-group reveal-item" style="--delay: 0.38s;">
          <label class="stationery-input-label" for="guestNum">Number of Guests Attending</label>
          <select id="guestNum" class="stationery-line-input stationery-select">
            <option value="2 Guests" selected>2 Guests (Both Attending)</option>
            <option value="1 Guest">1 Guest Attending</option>
          </select>
        </div>"""
            name_label = "Guest Names"
        else:
            pax_selector_html = ""
            name_label = "Guest Name"

        rsvp_section = f"""    <!-- RSVP Section (Pure Haute Couture Stationery) -->
    <section class="rsvp-editorial-section" id="rsvp">
      <h2 class="rsvp-headline reveal-item" style="--delay: 0.1s;">Confirm Attendance</h2>
      <p class="rsvp-lead reveal-item" style="--delay: 0.2s;">Please confirm your presence for each event of our wedding weekend:</p>

      <form id="weddingGuestForm" class="stationery-form" onsubmit="handleGuestSubmit(event)">
        
        {rsvp_events_html}
        <div class="stationery-input-group reveal-item" style="--delay: 0.35s;">
          <label class="stationery-input-label" for="guestName">{name_label}</label>
          <input type="text" id="guestName" class="stationery-line-input" value="{name}" required>
        </div>
        {pax_selector_html}
        <div class="stationery-input-group reveal-item" style="--delay: 0.42s;">
          <label class="stationery-input-label" for="guestNote">Dietary requirements or a message for Elia &amp; Daniel</label>
          <input type="text" id="guestNote" class="stationery-line-input" placeholder="Allergies, dietary preferences, or a personal note...">
        </div>

        <button type="submit" class="stationery-submit-btn reveal-item" style="--delay: 0.55s;">Send RSVP</button>
      </form>
    </section>

  </main>
"""

        # Build JavaScript logic with Google Sheets + FormSubmit parallel fast submit
        guest_footer = footer_base
        guest_footer = re.sub(r'Thank You Fausto!', f'Thank You {first_name}!', guest_footer)

        script_replacement = f"""  <script>
    const GOOGLE_SHEET_URL = 'https://script.google.com/macros/s/AKfycbwV6hHhModuKL82D3sEcVajyeP8saamvna6KW02E9mN6o7WBtll7LBvJiv4pIkembFd/exec';
    const hasFri = {str(has_fri).lower()};
    const hasSat = true;
    const hasSun = {str(has_sun).lower()};
    const isCouple = {str(is_couple).lower()};
    const maxParty = {party_size};

    const choices = {{
      1: hasFri,
      2: true,
      3: hasSun
    }};

    const LOOKBOOK_DATA = {{
      day1: {{
        img: '/assets/images/day1_attire.jpg',
        fallback: 'assets/images/day1_attire.jpg',
        tag: 'FRIDAY, APRIL 16 &middot; CIAMPINI',
        title: 'Roman Cocktail Chic',
        swatches: [
          {{ name: 'Italian Linen', color: '#D6C7B2' }},
          {{ name: 'Terracotta Silk', color: '#C05C3D' }},
          {{ name: 'Olive Green', color: '#5B6846' }},
          {{ name: 'Amber Sunset', color: '#D9823B' }}
        ],
        notes: `
          <p><strong>Gentlemen:</strong> Lightweight tailored blazers in linen, cotton, or fine summer wool in warm neutral tones (beige, tobacco, sage, navy). Dress trousers or tailored chinos, collared shirt (tie optional), and suede or leather loafers.</p><br>
          <p><strong>Ladies:</strong> Cocktail dresses, silk slip dresses, or elegant tailored jumpsuit separates in rich sunset and Roman earth tones (terracotta, amber, olive, champagne). Block heels or refined flats are recommended for cobblestone strolls around Trinità dei Monti.</p>
        `
      }},
      day2: {{
        img: '/assets/images/day2_attire.jpg',
        fallback: 'assets/images/day2_attire.jpg',
        tag: 'SATURDAY, APRIL 17 &middot; VATICAN & VILLA AURELIA',
        title: 'Black Tie Optional & Evening Gala',
        swatches: [
          {{ name: 'Classic Black', color: '#111111' }},
          {{ name: 'Midnight Navy', color: '#1B2430' }},
          {{ name: 'Emerald Green', color: '#0E3B2E' }},
          {{ name: 'Roman Gold', color: '#BFA175' }}
        ],
        notes: `
          <p><strong>Gentlemen:</strong> Classic black tuxedo with black bow tie, or a dark formal suit (midnight navy or charcoal) with an elegant silk tie and polished dress shoes.</p><br>
          <p><strong>Ladies:</strong> Floor-length evening gowns or sophisticated gala cocktail dresses in jewel tones, classic black, emerald, or deep sapphire, accented with fine jewelry.</p><br>
          <p><strong>*Vatican Chapel Modesty Requirement:</strong> For the religious blessing inside Cappella del Coro at St. Peter's Basilica, shoulders and knees must be respectfully covered. A matching silk scarf, shawl, or tailored jacket is ideal.</p>
        `
      }},
      day3: {{
        img: '/assets/images/day3_attire.jpg',
        fallback: 'assets/images/day3_attire.jpg',
        tag: 'SUNDAY, APRIL 18 &middot; HOTEL HASSLER',
        title: 'Sunday Casual Chic & Linens',
        swatches: [
          {{ name: 'Crisp Linen White', color: '#FFFFFF' }},
          {{ name: 'Travertine Sand', color: '#DFD5C6' }},
          {{ name: 'Sage Blossom', color: '#A3B19B' }},
          {{ name: 'Citrus Gold', color: '#E8C568' }}
        ],
        notes: `
          <p><strong>Gentlemen:</strong> Crisp white or pastel linen button-up shirts, relaxed tailored trousers or linen pants, woven belt, espadrilles or loafers, and sunglasses for rooftop terrace sunshine.</p><br>
          <p><strong>Ladies:</strong> Breezy sundresses, linen sets, floral garden dresses, stylish straw hats, and comfortable chic footwear for enjoying the morning vistas over the Spanish Steps.</p>
        `
      }}
    }};

    function setStationeryChoice(eventId, isAttending) {{
      choices[eventId] = isAttending;
    }}

    function openLookbook(dayKey) {{
      const data = LOOKBOOK_DATA[dayKey];
      if (!data) return;

      const imgEl = document.getElementById('modalLookbookImg');
      imgEl.src = data.img;
      imgEl.onerror = () => {{ imgEl.src = data.fallback; }};
      
      document.getElementById('modalLookbookTag').innerHTML = data.tag;
      document.getElementById('modalLookbookTitle').innerText = data.title;
      document.getElementById('modalLookbookNotes').innerHTML = data.notes;

      const swatchesContainer = document.getElementById('modalLookbookSwatches');
      swatchesContainer.innerHTML = data.swatches.map(s => `
        <div class="lookbook-swatch">
          <span class="swatch-dot" style="background: ${{s.color}};"></span>
          <span>${{s.name}}</span>
        </div>
      `).join('');

      document.getElementById('lookbookModal').classList.add('open');
    }}

    function closeLookbook() {{
      document.getElementById('lookbookModal').classList.remove('open');
    }}

    function closeConfirmModal() {{
      document.getElementById('confirmModal').classList.remove('open');
    }}

    function handleBackdropClick(e) {{
      if (e.target.classList.contains('modal-overlay')) {{
        e.target.classList.remove('open');
      }}
    }}

    async function handleGuestSubmit(e) {{
      e.preventDefault();
      const btn = e.target.querySelector('button[type="submit"]');
      const origText = btn.innerText;
      btn.disabled = true;
      btn.innerText = 'Sending RSVP...';

      const name = document.getElementById('guestName').value.trim();
      const numSelect = document.getElementById('guestNum');
      const attendingCount = numSelect ? (numSelect.value.includes('1') ? 1 : 2) : 1;
      const note = document.getElementById('guestNote') ? document.getElementById('guestNote').value.trim() : '';
      const submittedAt = new Date().toLocaleString('en-US', {{ timeZone: 'Europe/Rome' }});

      const isAnyAttending = (hasFri && choices[1]) || (hasSat && choices[2]) || (hasSun && choices[3]);

      const ciampiniStatus = hasFri ? (choices[1] ? 'Attending' : 'Decline') : '-';
      const weddingStatus = choices[2] ? 'Attending' : 'Decline';
      const brunchStatus = hasSun ? (choices[3] ? 'Attending' : 'Decline') : '-';

      const finalCount = isAnyAttending ? attendingCount : 0;

      const newEntry = {{
        id: 'rsvp_' + Date.now(),
        source: 'rome',
        event: 'Rome Wedding Weekend (16-18 Apr 2027)',
        guest: name,
        status: isAnyAttending ? 'Attending' : 'Declined',
        count: finalCount,
        party_size: maxParty,
        ciampini: ciampiniStatus,
        vatican_aurelia: weddingStatus,
        brunch: brunchStatus,
        diet: note || 'None',
        note: note || '',
        timestamp: submittedAt
      }};

      // 1. Local Storage backup (0ms)
      try {{
        const local = JSON.parse(localStorage.getItem('wedding_rsvps') || '[]');
        local.push(newEntry);
        localStorage.setItem('wedding_rsvps', JSON.stringify(local));
      }} catch (lErr) {{}}

      // 2. Google Sheets sync
      const sheetPromise = GOOGLE_SHEET_URL
        ? fetch(GOOGLE_SHEET_URL, {{
            method: 'POST',
            mode: 'no-cors',
            headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
            body: JSON.stringify(newEntry)
          }}).then(() => true).catch(() => false)
        : Promise.resolve(false);

      // 3. FormSubmit email backup
      const emailPayload = {{
        _subject: 'RSVP Rome: ' + name + ' (' + (isAnyAttending ? (finalCount + ' Attending') : 'Declined') + ')',
        _template: "table",
        _captcha: "false",
        "Guest(s)": name,
        "Party Count Attending": isAnyAttending ? (finalCount + (finalCount === 1 ? ' Person' : ' Persons')) : '0 (Declined)',
        "1. Welcome Dinner (16 Apr)": hasFri ? (choices[1] ? "YES (Attending)" : "NO (Decline)") : "Not Invited",
        "2. Vatican & Villa Aurelia (17 Apr)": choices[2] ? "YES (Attending)" : "NO (Decline)",
        "3. Hassler Brunch (18 Apr)": hasSun ? (choices[3] ? "YES (Attending)" : "NO (Decline)") : "Not Invited",
        "Dietary / Message": note || "None",
        "Date Submitted": submittedAt
      }};

      const emailPromise = fetch("https://formsubmit.co/ajax/elia.innamorati@gmail.com", {{
        method: "POST",
        headers: {{
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }},
        body: JSON.stringify(emailPayload)
      }}).then(r => r.ok).catch(() => false);

      // 4. Snappy race cap at 1.5s
      const timeoutPromise = new Promise(resolve => setTimeout(resolve, 1500));
      await Promise.race([
        Promise.all([sheetPromise, emailPromise]),
        timeoutPromise
      ]);

      btn.disabled = false;
      btn.innerText = origText;

      document.getElementById('confirmModal').classList.add('open');
    }}

    function initScrollReveals() {{
      const reveals = document.querySelectorAll('.reveal-item, .editorial-divider');
      if (!('IntersectionObserver' in window)) {{
        reveals.forEach(el => el.classList.add('is-visible'));
        return;
      }}

      const observer = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
          if (entry.isIntersecting) {{
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }}
        }});
      }}, {{
        threshold: 0.08,
        rootMargin: '0px 0px -30px 0px'
      }});

      reveals.forEach(el => observer.observe(el));
    }}

    if (document.readyState === 'loading') {{
      document.addEventListener('DOMContentLoaded', initScrollReveals);
    }} else {{
      initScrollReveals();
    }}

    function dismissPreloader() {{
      const preloader = document.getElementById('sitePreloader');
      if (preloader && !preloader.classList.contains('loaded')) {{
        preloader.classList.add('loaded');
        setTimeout(initScrollReveals, 100);
      }}
    }}

    window.addEventListener('load', () => {{
      setTimeout(dismissPreloader, 1800);
    }});
    setTimeout(dismissPreloader, 3200);
  </script>
</body>
</html>"""

        guest_footer = re.sub(r'<script>[\s\S]*?</html>', script_replacement, guest_footer)

        # Assemble Full Page HTML
        full_html = guest_head_hero + welcome_section + days_html + rsvp_section + guest_footer

        # 1. Save [slug].html in root directory
        out_root_file = os.path.join(BASE_DIR, f'{slug}.html')
        with open(out_root_file, 'w', encoding='utf-8') as out_f:
            out_f.write(full_html)

        # 2. Save [slug]/index.html for subfolder routing
        out_dir = os.path.join(BASE_DIR, slug)
        os.makedirs(out_dir, exist_ok=True)
        out_sub_file = os.path.join(out_dir, 'index.html')
        with open(out_sub_file, 'w', encoding='utf-8') as out_f:
            out_f.write(full_html)

        # Alias for fausto if needed
        if slug == 'fausto-innamorati':
            with open(os.path.join(BASE_DIR, 'fausto.html'), 'w', encoding='utf-8') as out_f:
                out_f.write(full_html)
            f_dir = os.path.join(BASE_DIR, 'fausto')
            os.makedirs(f_dir, exist_ok=True)
            with open(os.path.join(f_dir, 'index.html'), 'w', encoding='utf-8') as out_f:
                out_f.write(full_html)

        events_str = []
        if has_fri: events_str.append('Fri (Ciampini)')
        events_str.append('Sat (Wedding)')
        if has_sun: events_str.append('Sun (Brunch)')

        directory_entries.append({
            'order': inv['order'],
            'name': name,
            'slug': slug,
            'is_couple': is_couple,
            'party_size': party_size,
            'side': inv['side'],
            'group': inv['group'],
            'has_fri': has_fri,
            'has_sun': has_sun,
            'events_count': (1 if has_fri else 0) + 1 + (1 if has_sun else 0),
            'events': ' + '.join(events_str),
            'url': f'https://innamorati-meister.com/{slug}',
            'members': inv['members']
        })

    # Sort directory by order
    directory_entries.sort(key=lambda x: x['order'])

    # 3. Create graceful redirect pages for individual members of couples
    for c in COUPLES_CONFIG:
        couple_slug = c['slug']
        for member_name in c['members']:
            slug_variants = {
                slugify(member_name),
                slugify(member_name.replace("'", "-")),
                slugify(member_name.replace("'", ""))
            }
            for mem_slug in slug_variants:
                if not mem_slug or mem_slug == couple_slug:
                    continue
                redirect_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Redirecting to your invitation...</title>
  <meta http-equiv="refresh" content="0; url=/{couple_slug}">
  <link rel="canonical" href="https://innamorati-meister.com/{couple_slug}">
  <script>window.location.replace('/{couple_slug}');</script>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; padding: 25vh 1.5rem; background: #FAF9F6; color: #1A1918;">
  <p style="font-size: 1.2rem; margin-bottom: 1rem;">Redirecting to your wedding invitation...</p>
  <p><a href="/{couple_slug}" style="color: #BFA175; text-decoration: underline;">Click here if not redirected automatically &rarr;</a></p>
</body>
</html>"""
                # Root file
                with open(os.path.join(BASE_DIR, f'{mem_slug}.html'), 'w', encoding='utf-8') as rf:
                    rf.write(redirect_html)
                # Subfolder index.html
                mem_dir = os.path.join(BASE_DIR, mem_slug)
                os.makedirs(mem_dir, exist_ok=True)
                with open(os.path.join(mem_dir, 'index.html'), 'w', encoding='utf-8') as rf:
                    rf.write(redirect_html)

    # 4. Write Markdown invitation directory (INVITATIONS.md)
    md_file = os.path.join(BASE_DIR, 'INVITATIONS.md')
    with open(md_file, 'w', encoding='utf-8') as mf:
        mf.write('# 💌 Elia & Daniel — Rome Wedding Personalized Invitations\n\n')
        mf.write(f'**Total Invitations**: {len(directory_entries)} ({len([x for x in directory_entries if x["is_couple"]])} Couples + {len([x for x in directory_entries if not x["is_couple"]])} Solo) · **Total Guests**: 76\n\n')
        mf.write('| No. | Invitation Name | Type | Side | Events Invited | Personalized Link |\n')
        mf.write('|---|---|---|---|---|---|\n')
        for i, e in enumerate(directory_entries, 1):
            type_str = f"👥 Couple ({e['party_size']} Pax)" if e['is_couple'] else "👤 Solo (1 Pax)"
            mf.write(f"| {i} | **{e['name']}** | {type_str} | {e['side']} | {e['events']} | [{e['slug']}](https://innamorati-meister.com/{e['slug']}) |\n")

    # 5. Update guests.csv with all 76 guests
    csv_file = os.path.join(BASE_DIR, 'guests.csv')
    with open(csv_file, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.writer(cf)
        writer.writerow([
            'order', 'number', 'guest_name', 'is_couple', 'invitation_name',
            'invitation_slug', 'invitation_url', 'side', 'group',
            'party_size', 'friday_ciampini', 'saturday_wedding',
            'sunday_brunch', 'email', 'phone', 'notes'
        ])
        for g in guests:
            inv_name = g['name']
            if g.get('is_couple'):
                # Find couple display name
                for c in COUPLES_CONFIG:
                    if c['slug'] == g.get('couple_slug'):
                        inv_name = c['display_name']
                        break
            writer.writerow([
                g.get('order', ''),
                g.get('number', ''),
                g.get('name', ''),
                'YES' if g.get('is_couple') else 'NO',
                inv_name,
                g.get('invitation_slug', ''),
                g.get('invitation_url', ''),
                g.get('side', ''),
                g.get('group', ''),
                g.get('party_size', 1),
                'YES' if g.get('friday_ciampini') else 'NO',
                'YES' if g.get('saturday_wedding') else 'NO',
                'YES' if g.get('sunday_brunch') else 'NO',
                g.get('email', ''),
                g.get('phone', ''),
                g.get('notes', '')
            ])

    # 6. Build Interactive HTML Directory Page for 1-click link copying
    html_directory_file = os.path.join(BASE_DIR, 'guest-directory.html')
    html_dir_content = build_html_directory(directory_entries)
    with open(html_directory_file, 'w', encoding='utf-8') as hdf:
        hdf.write(html_dir_content)

    print(f'Successfully generated {len(directory_entries)} personalized invitations, INVITATIONS.md, guests.csv, and guest-directory.html!')

def build_html_directory(entries):
    rows_json = json.dumps(entries, ensure_ascii=False)
    couples_count = len([x for x in entries if x['is_couple']])
    solo_count = len([x for x in entries if not x['is_couple']])
    three_days_count = len([x for x in entries if x['events_count'] == 3])
    two_days_count = len([x for x in entries if x['events_count'] == 2])
    one_day_count = len([x for x in entries if x['events_count'] == 1])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Elia & Daniel — Wedding Guest Directory & Personalized Links</title>
  <link rel="icon" type="image/svg+xml" href="heart.svg">
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --font-serif: 'Cormorant Garamond', Georgia, serif;
      --font-sans: 'Inter', -apple-system, sans-serif;
      --color-bg: #FAF9F6;
      --color-white: #FFFFFF;
      --color-dark: #1A1918;
      --color-charcoal: #3A3836;
      --color-gold: #BFA175;
      --color-gold-hover: #9E825A;
      --color-border: #E8E2D8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font-sans);
      background-color: var(--color-bg);
      color: var(--color-dark);
      padding: 2.5rem 1.5rem;
      line-height: 1.5;
    }}
    .container {{
      max-width: 1180px;
      margin: 0 auto;
    }}
    header {{
      text-align: center;
      margin-bottom: 2.5rem;
    }}
    h1 {{
      font-family: var(--font-serif);
      font-size: clamp(2.4rem, 5vw, 3.4rem);
      font-weight: 400;
      color: var(--color-dark);
      margin-bottom: 0.5rem;
    }}
    .subtitle {{
      color: var(--color-gold);
      font-size: 0.95rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      font-weight: 500;
      margin-bottom: 1.5rem;
    }}
    .stats-bar {{
      display: flex;
      justify-content: center;
      gap: 1rem;
      flex-wrap: wrap;
      margin-bottom: 2rem;
    }}
    .stat-badge {{
      background: var(--color-white);
      border: 1px solid var(--color-border);
      border-radius: 30px;
      padding: 0.5rem 1.2rem;
      font-size: 0.85rem;
      color: var(--color-charcoal);
    }}
    .stat-badge strong {{
      color: var(--color-gold);
    }}
    .controls {{
      display: flex;
      gap: 1rem;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
      align-items: center;
    }}
    .search-box {{
      flex: 1;
      min-width: 250px;
      position: relative;
    }}
    .search-input {{
      width: 100%;
      padding: 0.75rem 1rem;
      border: 1px solid var(--color-border);
      border-radius: 8px;
      font-size: 0.95rem;
      font-family: var(--font-sans);
      outline: none;
      background: var(--color-white);
    }}
    .search-input:focus {{
      border-color: var(--color-gold);
    }}
    .filter-tabs {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}
    .tab-btn {{
      padding: 0.6rem 1rem;
      border: 1px solid var(--color-border);
      background: var(--color-white);
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.82rem;
      font-weight: 500;
      color: var(--color-charcoal);
      transition: all 0.2s;
    }}
    .tab-btn.active, .tab-btn:hover {{
      background: var(--color-gold);
      border-color: var(--color-gold);
      color: var(--color-white);
    }}
    .table-card {{
      background: var(--color-white);
      border: 1px solid var(--color-border);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.9rem;
    }}
    th {{
      background: #F4EFE8;
      padding: 1rem;
      font-weight: 600;
      color: var(--color-dark);
      border-bottom: 1px solid var(--color-border);
      font-size: 0.82rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }}
    td {{
      padding: 1rem;
      border-bottom: 1px solid var(--color-border);
      color: var(--color-charcoal);
    }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #FAF7F2; }}
    .guest-name {{
      font-weight: 600;
      color: var(--color-dark);
    }}
    .badge {{
      display: inline-block;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 500;
      margin-right: 0.3rem;
    }}
    .badge-couple {{ background: #F6EDF8; color: #7B3E8C; }}
    .badge-solo {{ background: #EDF3F7; color: #355E7A; }}
    .badge-3days {{ background: #EBF3EA; color: #2B6B27; }}
    .badge-2days {{ background: #EEF4F8; color: #23527C; }}
    .badge-1day {{ background: #F8F1E7; color: #8A5A1F; }}
    .actions {{
      display: flex;
      gap: 0.5rem;
    }}
    .btn-action {{
      padding: 0.45rem 0.85rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 500;
      text-decoration: none;
      cursor: pointer;
      border: 1px solid var(--color-border);
      background: var(--color-white);
      color: var(--color-dark);
      transition: all 0.2s;
    }}
    .btn-action:hover {{
      background: var(--color-gold);
      border-color: var(--color-gold);
      color: var(--color-white);
    }}
    .toast {{
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: #1A1918;
      color: #fff;
      padding: 0.8rem 1.4rem;
      border-radius: 8px;
      font-size: 0.9rem;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s;
      z-index: 999;
      box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }}
    .toast.show {{ opacity: 1; }}
  </style>
</head>
<body>

  <div class="container">
    <header>
      <h1>Elia & Daniel</h1>
      <div class="subtitle">Rome Wedding — Guest Directory & Personalized Links</div>
      
      <div class="stats-bar">
        <div class="stat-badge">Total Invitations: <strong>{len(entries)}</strong></div>
        <div class="stat-badge">Total Guests: <strong>76</strong></div>
        <div class="stat-badge">Couples: <strong>{couples_count}</strong></div>
        <div class="stat-badge">Solo: <strong>{solo_count}</strong></div>
        <div class="stat-badge">3 Days (Full Weekend): <strong>{three_days_count}</strong></div>
        <div class="stat-badge">2 Days (Sat + Sun): <strong>{two_days_count}</strong></div>
        <div class="stat-badge">Saturday Only: <strong>{one_day_count}</strong></div>
      </div>
    </header>

    <div class="controls">
      <div class="search-box">
        <input type="text" id="searchInput" class="search-input" placeholder="Search by name, side, or partner..." oninput="filterTable()">
      </div>
      <div class="filter-tabs">
        <button class="tab-btn active" onclick="setFilter('all', this)">All ({len(entries)})</button>
        <button class="tab-btn" onclick="setFilter('couples', this)">Couples ({couples_count})</button>
        <button class="tab-btn" onclick="setFilter('solo', this)">Solo ({solo_count})</button>
        <button class="tab-btn" onclick="setFilter('3days', this)">3 Days ({three_days_count})</button>
        <button class="tab-btn" onclick="setFilter('2days', this)">2 Days ({two_days_count})</button>
        <button class="tab-btn" onclick="setFilter('1day', this)">Sat Only ({one_day_count})</button>
        <button class="tab-btn" onclick="setFilter('daniel', this)">Daniel's Side</button>
        <button class="tab-btn" onclick="setFilter('elia', this)">Elia's Side</button>
      </div>
      <a href="guests.csv" download="wedding_guests.csv" class="btn-action" style="padding: 0.6rem 1.1rem; background: var(--color-gold); color: #fff; border-color: var(--color-gold); font-weight: 600; display: inline-flex; align-items: center; gap: 0.4rem;">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
        Download CSV
      </a>
    </div>

    <div class="table-card">
      <table>
        <thead>
          <tr>
            <th style="width: 45px;">No.</th>
            <th>Invitation &amp; Guests</th>
            <th>Party</th>
            <th>Side</th>
            <th>Invited Events</th>
            <th style="text-align: right;">Personalized Link</th>
          </tr>
        </thead>
        <tbody id="guestTableBody"></tbody>
      </table>
    </div>

    <div style="margin-top: 2rem; text-align: center; color: #8C8882; font-size: 0.85rem;">
      <p>💡 <strong>Tip for editing:</strong> You can edit <code>guests.csv</code> or <code>guests.json</code> at any time and run <code>python3 generate_invitations.py</code> to regenerate all pages in 1 second.</p>
    </div>
  </div>

  <div id="toast" class="toast">Link copied to clipboard!</div>

  <script>
    const data = {rows_json};
    let currentFilter = 'all';

    function renderTable() {{
      const tbody = document.getElementById('guestTableBody');
      const search = document.getElementById('searchInput').value.toLowerCase().trim();

      const filtered = data.filter(item => {{
        if (currentFilter === 'couples' && !item.is_couple) return false;
        if (currentFilter === 'solo' && item.is_couple) return false;
        if (currentFilter === '3days' && item.events_count !== 3) return false;
        if (currentFilter === '2days' && item.events_count !== 2) return false;
        if (currentFilter === '1day' && item.events_count !== 1) return false;
        if (currentFilter === 'daniel' && !item.side.includes('Daniel')) return false;
        if (currentFilter === 'elia' && !item.side.includes('Elia')) return false;

        if (search) {{
          const matchName = item.name.toLowerCase().includes(search);
          const matchSide = item.side.toLowerCase().includes(search);
          const matchSlug = item.slug.toLowerCase().includes(search);
          const matchMembers = item.members && item.members.some(m => m.toLowerCase().includes(search));
          if (!matchName && !matchSide && !matchSlug && !matchMembers) return false;
        }}
        return true;
      }});

      tbody.innerHTML = filtered.map((item, idx) => {{
        let badgeClass = 'badge-3days';
        let badgeText = '3 Days (Full Weekend)';
        if (item.events_count === 2) {{
          badgeClass = 'badge-2days';
          badgeText = '2 Days (Sat + Sun)';
        }} else if (item.events_count === 1) {{
          badgeClass = 'badge-1day';
          badgeText = 'Saturday Only';
        }}

        const partyBadge = item.is_couple 
          ? '<span class="badge badge-couple">Couple (2 Pax)</span>' 
          : '<span class="badge badge-solo">Solo (1 Pax)</span>';

        return `
          <tr>
            <td style="color: #8C8882;">${{idx + 1}}</td>
            <td>
              <div class="guest-name">${{item.name}}</div>
              <div style="font-size: 0.78rem; color: #8C8882;">/${{item.slug}}</div>
            </td>
            <td>${{partyBadge}}</td>
            <td>${{item.side}}</td>
            <td>
              <span class="badge ${{badgeClass}}">${{badgeText}}</span>
            </td>
            <td style="text-align: right;">
              <div class="actions" style="justify-content: flex-end;">
                <button class="btn-action" onclick="copyLink('${{item.url}}')">Copy Link</button>
                <a href="/${{item.slug}}" target="_blank" class="btn-action">Open &rarr;</a>
              </div>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function setFilter(filter, btn) {{
      currentFilter = filter;
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderTable();
    }}

    function filterTable() {{
      renderTable();
    }}

    function copyLink(url) {{
      navigator.clipboard.writeText(url).then(() => {{
        const toast = document.getElementById('toast');
        toast.innerText = 'Copied: ' + url;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2200);
      }});
    }}

    renderTable();
  </script>
</body>
</html>"""

if __name__ == '__main__':
    main()
