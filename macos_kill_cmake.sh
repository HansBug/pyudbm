# Check if cmake command exists
if command -v cmake >/dev/null 2>&1; then
    echo "Found CMake installation, proceeding with removal..."

    # Get the actual path of cmake
    CMAKE_PATH=$(which cmake)
    echo "CMake binary located at: $CMAKE_PATH"

    # Remove if installed via Homebrew
    if brew list cmake &>/dev/null; then
        echo "Removing CMake installed via Homebrew..."
        brew uninstall cmake
    fi

    # Remove common CMake installation directories
    echo "Removing CMake related directories..."
    sudo rm -rf /usr/local/cmake*
    sudo rm -rf /usr/local/share/cmake*
    sudo rm -rf /usr/local/doc/cmake*
    sudo rm -rf /usr/local/bin/cmake*
    sudo rm -rf /usr/local/lib/cmake*
    sudo rm -rf /usr/local/include/cmake*
    sudo rm -rf /Applications/CMake.app
    sudo rm -rf ~/Library/Application\ Support/CMake

    # Remove possible symbolic links
    sudo rm -f /usr/local/bin/cmake
    sudo rm -f /usr/local/bin/ctest
    sudo rm -f /usr/local/bin/cpack
    sudo rm -f /usr/local/bin/ccmake

    echo "CMake removal completed."

    # Verify cleanup results
    if command -v cmake >/dev/null 2>&1; then
        echo "Warning: CMake is still detected in the system. Manual inspection may be needed."
        which cmake
    else
        echo "Success: CMake has been completely removed from the system."
    fi
else
    echo "CMake is not installed on this system."
fi
