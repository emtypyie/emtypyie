name: pakuman
on:
  schedule: # Run automatically every 24 hours
    - cron: '0 0 * * *'
  workflow_dispatch: # Allows manual triggering
  push: # Runs on every push to the main branch
    branches:
      - main
jobs:
  generate:
    permissions:
      contents: write
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - name: checkout repo (for the overlay script)
        uses: actions/checkout@v4

      - name: generate contribution graph SVGs
        uses: abozanona/pacman-contribution-graph@main
        with:
          github_user_name: ${{ github.repository_owner }}
          # Comma-separated list of game names to generate. Default: pacman
          games: 'pacman'
          # Optional: omit the month labels row above the grid. Default: false
          hide_month_labels: 'false'

      - name: set up python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: inject blinking GAME OVER overlay into generated SVGs
        run: |
          for f in dist/*.svg; do
            echo "Processing $f"
            python3 scripts/add_game_over.py "$f"
          done

      # Push the generated SVGs to the output branch
      - name: push SVGs to the output branch
        uses: crazy-max/ghaction-github-pages@v3.1.0
        with:
          target_branch: output
          build_dir: dist
          keep_files: true # stops this from wiping out snake's files
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: print output svg links
        run: |
          echo "Pacman: https://raw.githubusercontent.com/${{ github.repository }}/output/pacman-contribution-graph.svg"
          echo "Pacman (dark): https://raw.githubusercontent.com/${{ github.repository }}/output/pacman-contribution-graph-dark.svg"
