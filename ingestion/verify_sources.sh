#!/bin/bash
# Nordic Source Verification Script - Bash Version
# Tests RSS feeds with curl

echo "================================================================================"
echo "NORDIC SOURCE VERIFICATION - Complete Coverage"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
swedish_working=0
swedish_total=0
finnish_working=0
finnish_total=0
norwegian_working=0
norwegian_total=0

test_rss_feed() {
    local url="$1"
    local name="$2"

    # Test with curl (HEAD request)
    http_code=$(curl -s -I --max-time 5 "$url" 2>/dev/null | head -1 | awk '{print $2}')

    if [ "$http_code" == "200" ] || [ "$http_code" == "304" ]; then
        echo -e "${GREEN}✅ WORKING${NC} - HTTP $http_code - $name"
        echo "   URL: $url"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} - HTTP $http_code - $name"
        echo "   URL: $url"
        return 1
    fi
}

# WAVE 1: Danish Twitter Sources
echo ""
echo "================================================================================"
echo "WAVE 1: DANISH TWITTER SOURCES (RSS.app)"
echo "================================================================================"
echo ""
echo "⚠️  3 sources with placeholder URLs need RSS.app feed generation:"
echo "   1. Syd- og Sønderjyllands Politi (@SjylPoliti)"
echo "   2. Midt- og Vestsjællands Politi (@MVSJPoliti)"
echo "   3. Sydsjællands og Lolland-Falsters Politi (@SSJ_LFPoliti)"
echo ""
echo "Action required: Generate feeds at https://rss.app for these Twitter handles"

# WAVE 2: Swedish Police Regions
echo ""
echo "================================================================================"
echo "WAVE 2: SWEDISH POLICE REGIONS (18 regions)"
echo "================================================================================"
echo ""

swedish_regions=(
    "vastra-gotaland:Västra Götaland (Gothenburg/Landvetter Airport)"
    "uppsala:Uppsala"
    "sodermanland:Södermanland"
    "ostergotland:Östergötland"
    "jonkoping:Jönköping"
    "kronoberg:Kronoberg"
    "kalmar:Kalmar"
    "gotland:Gotland"
    "blekinge:Blekinge"
    "halland:Halland"
    "varmland:Värmland"
    "orebro:Örebro"
    "vastmanland:Västmanland"
    "dalarna:Dalarna"
    "gavleborg:Gävleborg"
    "vasternorrland:Västernorrland"
    "jamtland:Jämtland"
    "vasterbotten:Västerbotten"
)

for region_data in "${swedish_regions[@]}"; do
    IFS=':' read -r region_slug region_name <<< "$region_data"
    url="https://polisen.se/aktuellt/rss/${region_slug}/handelser-rss---${region_slug}/"

    ((swedish_total++))
    if test_rss_feed "$url" "Polisen $region_name"; then
        ((swedish_working++))
    fi
    sleep 0.5  # Rate limiting
done

# WAVE 3: Finnish Police Departments
echo ""
echo "================================================================================"
echo "WAVE 3: FINNISH POLICE DEPARTMENTS (5 departments)"
echo "================================================================================"
echo ""

finnish_departments=(
    "eastern-finland:Eastern Finland"
    "lapland:Lapland (Rovaniemi Airport)"
    "oulu:Oulu (Oulu Airport)"
    "central-finland:Central Finland"
    "western-finland:Western Finland"
)

for dept_data in "${finnish_departments[@]}"; do
    IFS=':' read -r dept_slug dept_name <<< "$dept_data"
    url="https://poliisi.fi/en/${dept_slug}-police-department/-/asset_publisher/ZtAEeHB39Lxr/rss"

    ((finnish_total++))
    if test_rss_feed "$url" "Poliisi $dept_name"; then
        ((finnish_working++))
    fi
    sleep 0.5
done

# WAVE 4: Norwegian Media
echo ""
echo "================================================================================"
echo "WAVE 4: NORWEGIAN MEDIA (4 sources)"
echo "================================================================================"
echo ""

norwegian_sources=(
    "https://www.dagbladet.no/rss:Dagbladet"
    "https://www.tv2.no/rss:TV2 Norway"
    "https://www.nettavisen.no/rss:Nettavisen"
    "https://www.nrk.no/nyheter/siste.rss:NRK Regional News"
)

for source_data in "${norwegian_sources[@]}"; do
    IFS=':' read -r url name <<< "$source_data"

    ((norwegian_total++))
    if test_rss_feed "$url" "$name"; then
        ((norwegian_working++))
    fi
    sleep 0.5
done

# SUMMARY REPORT
echo ""
echo "================================================================================"
echo "VERIFICATION SUMMARY"
echo "================================================================================"
echo ""
echo "1. Danish Twitter Sources: 3 sources requiring RSS.app feed generation"
echo "   Status: PENDING - User action required"
echo ""
echo "2. Swedish Police Regions: $swedish_working/$swedish_total working"
if [ $swedish_working -gt 0 ]; then
    echo -e "   ${GREEN}✅ Ready to add $swedish_working new Swedish police sources${NC}"
else
    echo -e "   ${RED}❌ No working Swedish police feeds found${NC}"
fi
echo ""
echo "3. Finnish Police Departments: $finnish_working/$finnish_total working"
if [ $finnish_working -gt 0 ]; then
    echo -e "   ${GREEN}✅ Ready to add $finnish_working new Finnish police sources${NC}"
else
    echo -e "   ${RED}❌ No working Finnish police feeds found${NC}"
fi
echo ""
echo "4. Norwegian Media: $norwegian_working/$norwegian_total working"
if [ $norwegian_working -gt 0 ]; then
    echo -e "   ${GREEN}✅ Ready to add $norwegian_working new Norwegian media sources${NC}"
else
    echo -e "   ${RED}❌ No working Norwegian media feeds found${NC}"
fi
echo ""
echo "================================================================================"
total_new=$((swedish_working + finnish_working + norwegian_working))
echo "TOTAL NEW SOURCES READY TO ADD: $total_new"
echo "  - Swedish Police: $swedish_working"
echo "  - Finnish Police: $finnish_working"
echo "  - Norwegian Media: $norwegian_working"
echo "  - Danish Twitter: 0 (requires manual RSS.app setup)"
echo "================================================================================"
echo ""
echo "✅ Verification complete."
