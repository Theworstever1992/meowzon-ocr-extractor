#!/bin/bash

# ============================================================================
# Meowzon v3.0 GitHub Deployment Script
# ============================================================================
# This script automates the entire process of updating your GitHub repository
# with the new v3.0 code.
#
# Prerequisites:
# - Git installed and configured
# - GitHub repository already exists
# - You have push access to the repository
#
# Usage:
#   chmod +x deploy_to_github.sh
#   ./deploy_to_github.sh
# ============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Cat banner
echo -e "${PURPLE}"
cat << "EOF"
      /\_/\      
     ( o.o )     MEOWZON v3.0 
      > ^ <      GitHub Deployment
     /|   |\     
    (_|   |_)    
EOF
echo -e "${NC}"

# ============================================================================
# Configuration
# ============================================================================

REPO_URL="https://github.com/Theworstever1992/meowzon-ocr-extractor.git"
BACKUP_BRANCH="backup-v2.0"
MAIN_BRANCH="main"
VERSION_TAG="v3.0.0"

# ============================================================================
# Step 1: Check if we're in a git repository
# ============================================================================

echo -e "${CYAN}[Step 1/10] Checking git repository...${NC}"

if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not in a git repository!${NC}"
    echo ""
    echo "Please navigate to your repository folder first:"
    echo "  cd /path/to/meowzon-ocr-extractor"
    echo ""
    echo "Or clone the repository if you don't have it locally:"
    echo "  git clone $REPO_URL"
    echo "  cd meowzon-ocr-extractor"
    exit 1
fi

echo -e "${GREEN}✓ Git repository detected${NC}"

# ============================================================================
# Step 2: Check for uncommitted changes
# ============================================================================

echo -e "${CYAN}[Step 2/10] Checking for uncommitted changes...${NC}"

if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Warning: You have uncommitted changes${NC}"
    echo ""
    git status --short
    echo ""
    read -p "Do you want to continue? This will stash your changes. (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Deployment cancelled${NC}"
        exit 1
    fi
    git stash save "Auto-stash before v3.0 deployment"
    echo -e "${GREEN}✓ Changes stashed${NC}"
else
    echo -e "${GREEN}✓ Working directory clean${NC}"
fi

# ============================================================================
# Step 3: Fetch latest changes
# ============================================================================

echo -e "${CYAN}[Step 3/10] Fetching latest changes from remote...${NC}"

git fetch origin
echo -e "${GREEN}✓ Fetched latest changes${NC}"

# ============================================================================
# Step 4: Create backup branch
# ============================================================================

echo -e "${CYAN}[Step 4/10] Creating backup branch...${NC}"

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if git show-ref --verify --quiet "refs/heads/$BACKUP_BRANCH"; then
    echo -e "${YELLOW}⚠️  Backup branch '$BACKUP_BRANCH' already exists${NC}"
    read -p "Overwrite it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git branch -D $BACKUP_BRANCH
        echo -e "${GREEN}✓ Deleted old backup branch${NC}"
    fi
fi

if [ "$CURRENT_BRANCH" != "$MAIN_BRANCH" ]; then
    git checkout $MAIN_BRANCH
fi

git checkout -b $BACKUP_BRANCH
git push -f origin $BACKUP_BRANCH
echo -e "${GREEN}✓ Created and pushed backup branch: $BACKUP_BRANCH${NC}"

git checkout $MAIN_BRANCH

# ============================================================================
# Step 5: Remove old files
# ============================================================================

echo -e "${CYAN}[Step 5/10] Cleaning up old files...${NC}"

# Check if old monolithic file exists
if [ -f "meowzon_ocr_extractor.py" ]; then
    echo "Found old meowzon_ocr_extractor.py"
    read -p "Move to archive? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p archive
        git mv meowzon_ocr_extractor.py archive/
        echo -e "${GREEN}✓ Moved old file to archive/${NC}"
    else
        git rm meowzon_ocr_extractor.py
        echo -e "${GREEN}✓ Removed old file${NC}"
    fi
fi

echo -e "${GREEN}✓ Cleanup complete${NC}"

# ============================================================================
# Step 6: Verify new files exist
# ============================================================================

echo -e "${CYAN}[Step 6/10] Verifying new files...${NC}"

REQUIRED_FILES=(
    "main.py"
    "setup.py"
    "requirements.txt"
    "README.md"
    "meowzon/__init__.py"
    "meowzon/config.py"
    "meowzon/extractor.py"
)

MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    echo -e "${RED}❌ Error: Missing required files:${NC}"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "Please ensure all v3.0 files are in the repository directory."
    exit 1
fi

echo -e "${GREEN}✓ All required files present${NC}"

# ============================================================================
# Step 7: Add new files
# ============================================================================

echo -e "${CYAN}[Step 7/10] Adding new files to git...${NC}"

git add .
echo -e "${GREEN}✓ Added all files${NC}"

# Show what will be committed
echo ""
echo -e "${BLUE}Files to be committed:${NC}"
git status --short | head -20
echo ""

# ============================================================================
# Step 8: Commit changes
# ============================================================================

echo -e "${CYAN}[Step 8/10] Creating commit...${NC}"

COMMIT_MESSAGE="🎉 Major Release: Meowzon v3.0 - Complete Production Rewrite

✨ New Features:
- Modular architecture with 11+ specialized modules
- Multi-AI provider support (Ollama, OpenAI, Claude, Gemini)
- Parallel processing for 2-4x speed improvement
- Interactive review mode for manual corrections
- Rich analytics with automatic visualizations
- Multiple output formats (CSV, Excel, JSON, HTML)
- Duplicate detection and data validation
- Comprehensive error handling and logging
- YAML configuration support
- Professional package structure (pip installable)

📚 Documentation:
- Complete README with examples
- Quick start guide (5-minute setup)
- Architecture documentation
- Installation verification script
- Example configuration files

🔧 Technical Improvements:
- Type hints throughout
- Proper exception handling with retries
- Structured logging (console + file)
- Clean class hierarchy with mixins
- Factory patterns for extensibility
- Thread-safe parallel processing
- Comprehensive input validation

⚠️ Breaking Changes:
- Complete code restructure (v2.0 code backed up in '$BACKUP_BRANCH')
- New CLI interface and arguments
- New configuration system
- Different module structure

See CHANGELOG.md for complete details.

Co-authored-by: Claude <claude@anthropic.com>"

git commit -m "$COMMIT_MESSAGE"
echo -e "${GREEN}✓ Commit created${NC}"

# ============================================================================
# Step 9: Create tag
# ============================================================================

echo -e "${CYAN}[Step 9/10] Creating version tag...${NC}"

if git rev-parse "$VERSION_TAG" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Tag '$VERSION_TAG' already exists${NC}"
    read -p "Delete and recreate? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d $VERSION_TAG
        git push origin :refs/tags/$VERSION_TAG
        echo -e "${GREEN}✓ Deleted old tag${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipping tag creation${NC}"
        VERSION_TAG=""
    fi
fi

if [ -n "$VERSION_TAG" ]; then
    git tag -a $VERSION_TAG -m "Meowzon v3.0.0 - Production-Ready AI Hybrid OCR Extractor

Complete rewrite with professional architecture and extensive new features.

Highlights:
- Multi-AI support (4 providers)
- Parallel processing
- Interactive review mode
- Rich analytics and reporting
- Production-ready error handling

See release notes for full details."
    
    echo -e "${GREEN}✓ Tag created: $VERSION_TAG${NC}"
fi

# ============================================================================
# Step 10: Push to GitHub
# ============================================================================

echo -e "${CYAN}[Step 10/10] Pushing to GitHub...${NC}"
echo ""
echo -e "${YELLOW}This will push to: $REPO_URL${NC}"
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Push cancelled${NC}"
    echo ""
    echo "Your changes are committed locally but not pushed."
    echo "You can push manually later with:"
    echo "  git push origin $MAIN_BRANCH"
    if [ -n "$VERSION_TAG" ]; then
        echo "  git push origin $VERSION_TAG"
    fi
    exit 1
fi

echo ""
echo -e "${BLUE}Pushing to GitHub...${NC}"

# Push main branch
echo "Pushing $MAIN_BRANCH branch..."
git push origin $MAIN_BRANCH

# Push backup branch (already done, but confirm)
echo "Confirming backup branch..."
git push origin $BACKUP_BRANCH

# Push tag
if [ -n "$VERSION_TAG" ]; then
    echo "Pushing $VERSION_TAG tag..."
    git push origin $VERSION_TAG
fi

# ============================================================================
# Success!
# ============================================================================

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                   🎉 SUCCESS! 🎉                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Deployment Complete!${NC}"
echo ""
echo -e "${BLUE}📦 What was deployed:${NC}"
echo "   ✓ Main branch: $MAIN_BRANCH"
echo "   ✓ Backup branch: $BACKUP_BRANCH (with old code)"
if [ -n "$VERSION_TAG" ]; then
    echo "   ✓ Version tag: $VERSION_TAG"
fi
echo ""
echo -e "${BLUE}🔗 Next Steps:${NC}"
echo ""
echo "1. View your repository:"
echo "   https://github.com/Theworstever1992/meowzon-ocr-extractor"
echo ""
echo "2. Create a GitHub Release:"
echo "   https://github.com/Theworstever1992/meowzon-ocr-extractor/releases/new"
echo "   - Tag: $VERSION_TAG"
echo "   - Title: 🎉 Meowzon v3.0.0 - Production-Ready AI Hybrid Edition"
echo "   - Copy release notes from CHANGELOG.md or this script output"
echo ""
echo "3. Test the deployment:"
echo "   git clone $REPO_URL"
echo "   cd meowzon-ocr-extractor"
echo "   python test_installation.py"
echo ""
echo "4. Update repository settings:"
echo "   - Add description and topics"
echo "   - Enable GitHub Pages (optional)"
echo "   - Add badges to README"
echo ""
echo -e "${PURPLE}🐱 Meowzon v3.0 is now live! Happy extracting! 🐾${NC}"
echo ""
