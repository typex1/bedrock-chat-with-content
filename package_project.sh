#!/bin/bash

# Package Project Script
# Creates a tar.gz archive of the current directory while respecting .gitignore exclusions

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="$SCRIPT_DIR"  # Default to script directory
PROJECT_NAME="$(basename "$INPUT_DIR")"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
ARCHIVE_NAME="${PROJECT_NAME}_${TIMESTAMP}.tar.gz"
TEMP_EXCLUDE_FILE="/tmp/tar_exclude_$$"
S3_PATH=""  # S3 destination path (optional)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to validate S3 path format
validate_s3_path() {
    local s3_path="$1"
    
    if [[ ! "$s3_path" =~ ^s3://[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9](/.*)?$ ]]; then
        print_error "Invalid S3 path format. Expected: s3://bucket-name/path"
        print_error "Example: s3://mybucket/backups"
        return 1
    fi
    
    return 0
}

# Function to check AWS CLI availability and credentials
check_aws_cli() {
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed or not in PATH"
        print_error "Please install AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        return 1
    fi
    
    # Check AWS credentials
    print_status "Checking AWS credentials..."
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured or invalid"
        print_error "Please configure AWS credentials using:"
        print_error "  aws configure"
        print_error "  or set AWS_PROFILE environment variable"
        print_error "  or use IAM roles/instance profiles"
        return 1
    fi
    
    local caller_identity=$(aws sts get-caller-identity --output text --query 'Account')
    print_status "AWS Account: $caller_identity"
    return 0
}

# Function to upload archive to S3
upload_to_s3() {
    local archive_file="$1"
    local s3_destination="$2"
    
    print_status "Uploading archive to S3..."
    print_status "Source: $archive_file"
    print_status "Destination: $s3_destination"
    
    # Extract bucket and key from S3 path
    local bucket=$(echo "$s3_destination" | sed 's|s3://||' | cut -d'/' -f1)
    local key_prefix=$(echo "$s3_destination" | sed 's|s3://||' | cut -d'/' -f2-)
    
    # If key_prefix is empty or same as bucket, use root
    if [[ -z "$key_prefix" || "$key_prefix" == "$bucket" ]]; then
        key_prefix=""
    else
        # Ensure key_prefix ends with /
        if [[ ! "$key_prefix" =~ /$ ]]; then
            key_prefix="$key_prefix/"
        fi
    fi
    
    local s3_key="${key_prefix}$(basename "$archive_file")"
    local full_s3_path="s3://$bucket/$s3_key"
    
    print_status "S3 Key: $s3_key"
    
    # Check if bucket exists and is accessible
    if ! aws s3 ls "s3://$bucket" &> /dev/null; then
        print_error "Cannot access S3 bucket: $bucket"
        print_error "Please check:"
        print_error "  - Bucket exists"
        print_error "  - You have appropriate permissions"
        print_error "  - Bucket name is correct"
        return 1
    fi
    
    # Upload file with progress
    if aws s3 cp "$archive_file" "$full_s3_path" --no-progress; then
        print_success "Successfully uploaded to S3!"
        print_success "S3 Location: $full_s3_path"
        
        # Get file size in S3 for verification
        local s3_size=$(aws s3 ls "$full_s3_path" --human-readable | awk '{print $3 " " $4}')
        print_status "S3 File Size: $s3_size"
        
        return 0
    else
        print_error "Failed to upload to S3"
        return 1
    fi
}

# Function to clean up temporary files
cleanup() {
    if [[ -f "$TEMP_EXCLUDE_FILE" ]]; then
        rm -f "$TEMP_EXCLUDE_FILE"
    fi
}

# Set up cleanup trap
trap cleanup EXIT

# Function to convert .gitignore patterns to tar exclude patterns
process_gitignore() {
    local gitignore_file="$1"
    local exclude_file="$2"
    
    print_status "Processing .gitignore patterns..."
    
    # Clear the exclude file
    > "$exclude_file"
    
    # Process each line in .gitignore
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        
        # Remove leading/trailing whitespace
        line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # Skip if line is empty after trimming
        if [[ -z "$line" ]]; then
            continue
        fi
        
        # Handle different gitignore patterns
        if [[ "$line" == /* ]]; then
            # Pattern starts with / - relative to root
            pattern="${line#/}"
        elif [[ "$line" == */* ]]; then
            # Pattern contains / - treat as path pattern
            pattern="$line"
        else
            # Simple filename/dirname - match anywhere
            pattern="$line"
        fi
        
        # Remove trailing slash if present
        pattern="${pattern%/}"
        
        # Add to exclude file
        echo "$pattern" >> "$exclude_file"
        
        # Also add pattern with trailing /* to exclude directory contents
        if [[ ! "$pattern" == */ ]]; then
            echo "$pattern/*" >> "$exclude_file"
        fi
        
    done < "$gitignore_file"
    
    # Add common exclusions that should always be excluded
    cat >> "$exclude_file" << 'EOF'
.git
.git/*
*.tar.gz
*.zip
.DS_Store
Thumbs.db
EOF
}

# Main execution
main() {
    print_status "Starting project packaging..."
    print_status "Input directory: $INPUT_DIR"
    print_status "Archive name: $ARCHIVE_NAME"
    
    # Validate input directory exists
    if [[ ! -d "$INPUT_DIR" ]]; then
        print_error "Input directory does not exist: $INPUT_DIR"
        exit 1
    fi
    
    # If S3 path is specified, validate it and check AWS CLI
    if [[ -n "$S3_PATH" ]]; then
        print_status "S3 upload requested: $S3_PATH"
        
        if ! validate_s3_path "$S3_PATH"; then
            exit 1
        fi
        
        if ! check_aws_cli; then
            exit 1
        fi
    fi
    
    # Get absolute path for input directory
    INPUT_DIR="$(cd "$INPUT_DIR" && pwd)"
    print_status "Absolute path: $INPUT_DIR"
    
    # Change to input directory
    cd "$INPUT_DIR"
    
    # Check if .gitignore exists
    if [[ -f ".gitignore" ]]; then
        print_status "Found .gitignore file, processing exclusions..."
        process_gitignore ".gitignore" "$TEMP_EXCLUDE_FILE"
        
        # Show what will be excluded
        print_status "Exclusion patterns:"
        while IFS= read -r pattern; do
            echo "  - $pattern"
        done < "$TEMP_EXCLUDE_FILE"
        
        # Create archive with exclusions
        print_status "Creating archive with exclusions..."
        tar --exclude-from="$TEMP_EXCLUDE_FILE" -czf "$ARCHIVE_NAME" .
        
    else
        print_warning "No .gitignore file found, creating archive with basic exclusions..."
        
        # Create basic exclusions
        cat > "$TEMP_EXCLUDE_FILE" << 'EOF'
.git
.git/*
*.tar.gz
*.zip
.DS_Store
Thumbs.db
__pycache__
__pycache__/*
*.pyc
*.pyo
venv
venv/*
.venv
.venv/*
env
env/*
.env
node_modules
node_modules/*
EOF
        
        # Create archive with basic exclusions
        tar --exclude-from="$TEMP_EXCLUDE_FILE" -czf "$ARCHIVE_NAME" .
    fi
    
    # Check if archive was created successfully
    if [[ -f "$ARCHIVE_NAME" ]]; then
        ARCHIVE_SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
        print_success "Archive created successfully!"
        print_success "File: $ARCHIVE_NAME"
        print_success "Size: $ARCHIVE_SIZE"
        
        # Show archive contents summary
        print_status "Archive contents summary:"
        tar -tzf "$ARCHIVE_NAME" | head -20
        
        TOTAL_FILES=$(tar -tzf "$ARCHIVE_NAME" | wc -l)
        if [[ $TOTAL_FILES -gt 20 ]]; then
            print_status "... and $((TOTAL_FILES - 20)) more files"
        fi
        print_status "Total files in archive: $TOTAL_FILES"
        
        # Upload to S3 if requested
        if [[ -n "$S3_PATH" ]]; then
            if upload_to_s3 "$ARCHIVE_NAME" "$S3_PATH"; then
                print_status "Archive successfully uploaded to S3"
                
                # Ask if user wants to delete local archive
                echo
                read -p "Delete local archive file? [y/N]: " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    rm -f "$ARCHIVE_NAME"
                    print_status "Local archive deleted"
                else
                    print_status "Local archive retained: $ARCHIVE_NAME"
                fi
            else
                print_error "S3 upload failed, keeping local archive: $ARCHIVE_NAME"
                exit 1
            fi
        fi
        
    else
        print_error "Failed to create archive!"
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
Package Project Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help      Show this help message
    -i, --input     Specify input directory to package (default: current script directory)
    -n, --name      Specify custom archive name (without .tar.gz extension)
    -o, --output    Specify output directory for the archive
    -s, --s3        Upload archive to S3 (format: s3://bucket/path)

EXAMPLES:
    $0                                              # Package current script directory
    $0 -i /path/to/project                         # Package specified directory
    $0 -i ../other-project -n backup               # Package other directory with custom name
    $0 -i ~/Documents/myapp -o /tmp                # Package directory and save to /tmp
    $0 -s s3://mybucket/backups                    # Package and upload to S3
    $0 -i ~/project -s s3://mybucket/backups       # Package specific dir and upload to S3
    $0 -n production -s s3://mybucket/prod         # Custom name and S3 upload
    $0 -i ~/app -n backup -s s3://bucket/folder    # Full example with all options

S3 UPLOAD REQUIREMENTS:
    - AWS CLI must be installed and configured
    - Valid AWS credentials (via aws configure, environment variables, or IAM roles)
    - Appropriate S3 permissions (s3:PutObject, s3:ListBucket)
    - S3 bucket must exist and be accessible

S3 PATH FORMAT:
    s3://bucket-name/optional/path
    Examples:
        s3://mybucket                    # Upload to bucket root
        s3://mybucket/backups           # Upload to backups folder
        s3://mybucket/projects/2024     # Upload to nested folder

DESCRIPTION:
    This script creates a tar.gz archive of a specified directory while
    respecting .gitignore exclusions. If no .gitignore is found, it uses
    common exclusion patterns for development projects.
    
    The input directory can be specified with -i option, allowing you to
    package any directory from anywhere on your system.
    
    With the -s option, the archive can be automatically uploaded to AWS S3
    after creation, with an option to delete the local copy.

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -i|--input)
            if [[ -n "$2" && ! "$2" =~ ^- ]]; then
                INPUT_DIR="$2"
                # Update project name based on input directory
                PROJECT_NAME="$(basename "$INPUT_DIR")"
                # Update archive name if it hasn't been customized
                if [[ "$ARCHIVE_NAME" == *"_${TIMESTAMP}.tar.gz" ]]; then
                    ARCHIVE_NAME="${PROJECT_NAME}_${TIMESTAMP}.tar.gz"
                fi
                shift 2
            else
                print_error "Option -i requires a directory path"
                exit 1
            fi
            ;;
        -n|--name)
            if [[ -n "$2" && ! "$2" =~ ^- ]]; then
                ARCHIVE_NAME="$2.tar.gz"
                shift 2
            else
                print_error "Option -n requires a value"
                exit 1
            fi
            ;;
        -o|--output)
            if [[ -n "$2" && ! "$2" =~ ^- ]]; then
                OUTPUT_DIR="$2"
                if [[ ! -d "$OUTPUT_DIR" ]]; then
                    print_error "Output directory does not exist: $OUTPUT_DIR"
                    exit 1
                fi
                ARCHIVE_NAME="$OUTPUT_DIR/$ARCHIVE_NAME"
                shift 2
            else
                print_error "Option -o requires a value"
                exit 1
            fi
            ;;
        -s|--s3)
            if [[ -n "$2" && ! "$2" =~ ^- ]]; then
                S3_PATH="$2"
                shift 2
            else
                print_error "Option -s requires an S3 path (e.g., s3://mybucket/folder)"
                exit 1
            fi
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main
