"""
HTML and JavaScript templates for VIN GUI application using Tailwind CSS
"""


def get_html_template():
    """Return the main HTML template with Tailwind CSS"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIN Manual Entry</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            ibm: {
              blue: '#0f62fe',
              'blue-dark': '#0043ce',
              'gray-10': '#f4f4f4',
              'gray-20': '#e0e0e0',
              'gray-30': '#c6c6c6',
              'gray-40': '#a8a8a8',
              'gray-50': '#8d8d8d',
              'gray-60': '#6f6f6f',
              'gray-70': '#525252',
              'gray-80': '#393939',
              'gray-90': '#262626',
              'gray-100': '#161616',
              green: '#24a148',
              yellow: '#f1c21b',
              red: '#da1e28'
            }
          },
          fontFamily: {
            sans: ['"IBM Plex Sans"', 'sans-serif'],
            mono: ['"IBM Plex Mono"', 'monospace']
          }
        }
      }
    };
    </script>
</head>
<body class="bg-ibm-gray-10 text-ibm-gray-100 font-sans h-screen flex flex-col">
    <div class="grid grid-cols-1 md:grid-cols-[1fr,300px] grid-rows-[auto,1fr,auto] h-screen max-h-screen overflow-hidden">
        <!-- Header -->
        <header class="col-span-full bg-ibm-gray-100 text-white p-4 flex justify-between items-center shadow">
            <h1 class="text-xl font-normal">VIN Manual Entry</h1>
            <div class="flex gap-4 text-sm text-ibm-gray-30">
                <span id="status">Ready</span>
                <span id="counter">0 of 0 processed</span>
            </div>
        </header>

        <!-- Main Content -->
        <main class="p-4 overflow-y-auto flex flex-col gap-6">
            <!-- Image Controls -->
            <div class="flex bg-ibm-gray-80 text-white rounded overflow-hidden">
                <div class="flex-1 p-2 text-center cursor-pointer transition-colors text-sm shortcut-button active" data-mode="original">Original (1)</div>
                <div class="flex-1 p-2 text-center cursor-pointer transition-colors text-sm shortcut-button" data-mode="bw">B&W (2)</div>
                <div class="flex-1 p-2 text-center cursor-pointer transition-colors text-sm shortcut-button" data-mode="contrast">Contrast (3)</div>
                <div class="flex-1 p-2 text-center cursor-pointer transition-colors text-sm shortcut-button" data-mode="sharp">Sharp (4)</div>
            </div>

            <!-- Image Container -->
            <div class="bg-white border border-ibm-gray-30 rounded overflow-hidden flex flex-col">
                <div id="current-image" class="flex items-center justify-center min-h-[400px] max-h-[calc(100vh-350px)] overflow-hidden bg-ibm-gray-90">
                    <div class="text-ibm-gray-50 text-center p-8">No images loaded</div>
                </div>
                <div class="flex justify-between p-3 bg-ibm-gray-20 border-t border-ibm-gray-30 text-sm">
                    <span id="image-name">No image selected</span>
                    <span id="image-count"></span>
                </div>
            </div>

            <!-- Entry Form -->
            <div class="bg-white border border-ibm-gray-30 rounded p-6">
                <div class="mb-6">
                    <label for="vin-input" class="block mb-2 font-medium">Enter last 6 characters of VIN:</label>
                    <div class="flex flex-col md:flex-row gap-3">
                        <input type="text" id="vin-input" maxlength="6" autocomplete="off" placeholder="e.g. 583696"
                               class="flex-1 p-3 border-2 border-ibm-gray-30 rounded font-mono text-lg tracking-wider uppercase focus:outline-none focus:border-ibm-blue focus:ring-2 focus:ring-ibm-blue/20">
                        <button id="submit-btn" class="bg-ibm-blue hover:bg-ibm-blue-dark text-white font-medium p-3 rounded transition-colors">Save & Next</button>
                        <button id="skip-btn" class="bg-ibm-gray-20 hover:bg-ibm-gray-30 text-ibm-gray-80 font-medium p-3 rounded transition-colors">Skip</button>
                        <button id="delete-btn" class="bg-ibm-red hover:bg-ibm-red/90 text-white font-medium p-3 rounded transition-colors">Delete (Del)</button>
                    </div>
                    <div id="message" class="mt-4 h-6 transition-all"></div>
                </div>

                <!-- Keyboard Shortcuts -->
                <div class="border-t border-ibm-gray-30 pt-6">
                    <h3 class="text-sm mb-3 font-medium text-ibm-gray-70">Keyboard Shortcuts</h3>
                    <ul class="grid grid-cols-1 md:grid-cols-2 gap-2">
                        <li class="text-xs text-ibm-gray-60"><kbd class="font-mono bg-ibm-gray-20 px-1.5 py-0.5 rounded border border-ibm-gray-30 text-xs">Enter</kbd> Save and go to next image</li>
                        <li class="text-xs text-ibm-gray-60"><kbd class="font-mono bg-ibm-gray-20 px-1.5 py-0.5 rounded border border-ibm-gray-30 text-xs">Tab</kbd> then <kbd class="font-mono bg-ibm-gray-20 px-1.5 py-0.5 rounded border border-ibm-gray-30 text-xs">Enter</kbd> Skip current image</li>
                        <li class="text-xs text-ibm-gray-60"><kbd class="font-mono bg-ibm-gray-20 px-1.5 py-0.5 rounded border border-ibm-gray-30 text-xs">←</kbd> Previous image</li>
                        <li class="text-xs text-ibm-gray-60"><kbd class="font-mono bg-ibm-gray-20 px-1.5 py-0.5 rounded border border-ibm-gray-30 text-xs">→</kbd> Next image</li>
                        <li class="text-xs text-ibm-gray-60"><kbd class="font-mono bg-ibm-gray-20 px-1.5 py-0.5 rounded border border-ibm-gray-30 text-xs">1-4</kbd> Change image view mode</li>
                        <li class="text-xs text-ibm-gray-60"><kbd class="font-mono bg-ibm-gray-20 px-1.5 py-0.5 rounded border border-ibm-gray-30 text-xs">Del</kbd> Delete current image</li>
                        <li class="text-xs text-ibm-gray-60"><kbd class="font-mono bg-ibm-gray-20 px-1.5 py-0.5 rounded border border-ibm-gray-30 text-xs">Esc</kbd> Cancel/Close dialog</li>
                    </ul>
                </div>
            </div>
        </main>

        <!-- Sidebar -->
        <aside class="bg-ibm-gray-20 border-l border-ibm-gray-30 overflow-y-auto flex flex-col">
            <!-- Progress Section -->
            <div class="p-4 border-b border-ibm-gray-30">
                <h2 class="text-base font-medium mb-3">Affidavit Progress</h2>
                <div class="h-3 bg-ibm-gray-30 rounded-full overflow-hidden mb-4">
                    <div class="h-full bg-ibm-blue transition-all duration-300" id="progress-bar" style="width: 0%"></div>
                </div>
                <div class="flex justify-between text-sm text-ibm-gray-70">
                    <span id="stats-matched">0 Matched</span>
                    <span id="stats-pending">0 Pending</span>
                </div>
            </div>

            <!-- VIN List Section -->
            <div class="p-4 border-b border-ibm-gray-30">
                <h2 class="text-base font-medium mb-3">VIN Numbers</h2>
                <div class="max-h-[200px] overflow-y-auto mt-2 border border-ibm-gray-30 rounded" id="vin-list">
                    <div class="p-4 text-ibm-gray-60 italic">Loading VINs...</div>
                </div>
            </div>

            <!-- Images Section -->
            <div class="p-4 border-b border-ibm-gray-30 flex-1 flex flex-col">
                <h2 class="text-base font-medium mb-3">Images</h2>
                <div class="flex-1 overflow-y-auto image-list" id="image-list">
                    <div class="p-4 text-ibm-gray-60 italic">Loading images...</div>
                </div>
            </div>
        </aside>

        <!-- Footer -->
        <footer class="col-span-full bg-ibm-gray-20 border-t border-ibm-gray-30 p-3 text-sm text-ibm-gray-80">
            <div class="flex justify-between">
                <span>VIN Manual Entry v1.0.0</span>
                <span>Files will be saved to: <code class="font-mono bg-ibm-gray-20 px-1.5 py-0.5 rounded text-xs" id="save-path">processed_images</code></span>
            </div>
        </footer>
    </div>

    <!-- Duplicate VIN Modal -->
    <div class="fixed inset-0 bg-ibm-gray-100/70 flex items-center justify-center z-50 hidden" id="duplicate-modal">
        <div class="bg-white rounded-lg w-11/12 max-w-4xl max-h-[90vh] overflow-hidden flex flex-col shadow-xl">
            <div class="bg-ibm-gray-90 text-white p-4 flex justify-between items-center">
                <h2 class="text-xl font-normal">Duplicate VIN Detected</h2>
                <button class="text-ibm-gray-30 hover:text-white bg-transparent border-none text-2xl cursor-pointer px-2" id="modal-close">&times;</button>
            </div>
            <div class="p-6 overflow-y-auto">
                <p class="mb-4">VIN already exists in processed files. Choose which image to keep:</p>
                <div class="flex flex-col md:flex-row gap-4">
                    <div class="flex-1 text-center">
                        <div class="border border-ibm-gray-30 rounded-md overflow-hidden mb-2" id="existing-image">
                            <!-- Existing image will be inserted here -->
                        </div>
                        <div class="text-sm text-ibm-gray-70">Existing Image (1)</div>
                    </div>
                    <div class="flex-1 text-center">
                        <div class="border border-ibm-gray-30 rounded-md overflow-hidden mb-2" id="new-image">
                            <!-- New image will be inserted here -->
                        </div>
                        <div class="text-sm text-ibm-gray-70">New Image (2)</div>
                    </div>
                </div>
            </div>
            <div class="p-4 bg-ibm-gray-20 flex justify-end gap-3 border-t border-ibm-gray-30">
                <button class="bg-ibm-gray-20 hover:bg-ibm-gray-30 text-ibm-gray-80 font-medium px-5 py-3 rounded transition-colors" id="modal-cancel">Cancel (Esc)</button>
                <button class="bg-ibm-blue hover:bg-ibm-blue-dark text-white font-medium px-5 py-3 rounded transition-colors" id="keep-existing">Keep Existing (1)</button>
                <button class="bg-ibm-blue hover:bg-ibm-blue-dark text-white font-medium px-5 py-3 rounded transition-colors" id="keep-new">Keep New (2)</button>
            </div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Elements
        const imageList = document.getElementById('image-list');
        const currentImage = document.getElementById('current-image');
        const imageName = document.getElementById('image-name');
        const imageCount = document.getElementById('image-count');
        const vinInput = document.getElementById('vin-input');
        const submitBtn = document.getElementById('submit-btn');
        const skipBtn = document.getElementById('skip-btn');
        const deleteBtn = document.getElementById('delete-btn');
        const messageEl = document.getElementById('message');
        const statusEl = document.getElementById('status');
        const counterEl = document.getElementById('counter');
        const savePathEl = document.getElementById('save-path');
        const progressBar = document.getElementById('progress-bar');
        const statsMatched = document.getElementById('stats-matched');
        const statsPending = document.getElementById('stats-pending');
        const vinList = document.getElementById('vin-list');
        const shortcutButtons = document.querySelectorAll('.shortcut-button');

        // Modal elements
        const duplicateModal = document.getElementById('duplicate-modal');
        const modalClose = document.getElementById('modal-close');
        const modalCancel = document.getElementById('modal-cancel');
        const keepExisting = document.getElementById('keep-existing');
        const keepNew = document.getElementById('keep-new');
        const existingImage = document.getElementById('existing-image');
        const newImage = document.getElementById('new-image');

        // State
        let images = [];
        let currentIndex = 0;
        let processedCount = 0;
        let vinData = { vins: [], matched: [], pending: [] };
        let currentImageMode = 'original';
        let duplicateResolveCallback = null;

        // Set processed_images path
        savePathEl.textContent = 'processed_images';

        // Load images and VIN data
        async function loadData() {
            try {
                statusEl.textContent = 'Loading data...';

                // Load images
                const imagesResponse = await fetch('/api/images');
                const imagesData = await imagesResponse.json();

                images = imagesData.images;
                processedCount = imagesData.processed_count || 0;

                // Load VIN data
                const vinResponse = await fetch('/api/vins');
                const vinResult = await vinResponse.json();

                vinData = vinResult;

                // Render UI components
                renderImageList();
                renderVinList();
                updateProgress();

                if (images.length > 0) {
                    selectImage(0);
                    statusEl.textContent = 'Ready';
                    imageCount.textContent = `${currentIndex + 1} of ${images.length}`;
                    counterEl.textContent = `${processedCount} of ${images.length} processed`;
                } else {
                    statusEl.textContent = 'No images found';
                    imageList.innerHTML = '<div class="p-4 text-ibm-gray-60 italic">No images found in directory</div>';
                }
            } catch (error) {
                console.error('Error loading data:', error);
                statusEl.textContent = 'Error loading data';
                imageList.innerHTML = '<div class="p-4 text-ibm-gray-60 italic">Error loading images</div>';
                vinList.innerHTML = '<div class="p-4 text-ibm-gray-60 italic">Error loading VIN data</div>';
            }
        }

        // Render image list
        function renderImageList() {
            imageList.innerHTML = '';

            images.forEach((image, index) => {
                const item = document.createElement('div');
                item.className = 'py-3 px-4 border-b border-ibm-gray-30 cursor-pointer text-sm whitespace-nowrap overflow-hidden text-ellipsis transition-colors';

                if (index === currentIndex) {
                    item.classList.add('bg-ibm-blue', 'text-white');
                }

                // Check if this image has been processed
                if (isImageProcessed(image)) {
                    item.classList.add('text-ibm-gray-50', 'line-through');
                }

                item.textContent = image;
                item.addEventListener('click', () => selectImage(index));
                imageList.appendChild(item);
            });
        }

        // Render VIN list
        function renderVinList() {
            vinList.innerHTML = '';

            // First show matched VINs
            vinData.matched.forEach(vin => {
                const item = document.createElement('div');
                item.className = 'p-2 border-b border-ibm-gray-30 text-sm flex items-center bg-green-50/10';
                item.innerHTML = `<div class="w-2 h-2 rounded-full bg-ibm-green mr-2"></div>${vin}`;
                vinList.appendChild(item);
            });

            // Then show pending VINs
            vinData.pending.forEach(vin => {
                const item = document.createElement('div');
                item.className = 'p-2 border-b border-ibm-gray-30 text-sm flex items-center bg-yellow-50/10';
                item.innerHTML = `<div class="w-2 h-2 rounded-full bg-ibm-yellow mr-2"></div>${vin}`;
                vinList.appendChild(item);
            });

            if (vinData.matched.length === 0 && vinData.pending.length === 0) {
                vinList.innerHTML = '<div class="p-4 text-ibm-gray-60 italic">No VIN data available</div>';
            }
        }

        // Update progress indicators
        function updateProgress() {
            const total = vinData.vins.length || images.length;
            const matched = vinData.matched.length || processedCount;

            // Update progress bar
            const percentage = total > 0 ? (matched / total) * 100 : 0;
            progressBar.style.width = `${percentage}%`;

            // Update stats
            statsMatched.textContent = `${matched} Matched`;
            statsPending.textContent = `${total - matched} Pending`;
        }

        // Check if an image has been processed
        function isImageProcessed(filename) {
            const vin = extractVinFromFilename(filename);
            return vin && vinData.matched.includes(vin);
        }

        // Try to extract VIN from filename
        function extractVinFromFilename(filename) {
            const match = filename.match(/[A-Z0-9]{6}/i);
            return match ? match[0].toUpperCase() : null;
        }

        // Select an image
        function selectImage(index) {
            if (index < 0 || index >= images.length) return;

            currentIndex = index;
            const filename = images[currentIndex];

            // Update UI
            const items = imageList.querySelectorAll('.image-list > div');
            items.forEach(item => {
                item.classList.remove('bg-ibm-blue', 'text-white');
            });

            if (items[currentIndex]) {
                items[currentIndex].classList.add('bg-ibm-blue', 'text-white');
            }

            imageName.textContent = filename;
            imageCount.textContent = `${currentIndex + 1} of ${images.length}`;

            // Load image with timestamp to prevent caching
            loadImageWithMode(filename, currentImageMode);

            // Clear input and message
            vinInput.value = '';
            messageEl.textContent = '';
            messageEl.className = 'mt-4 h-6 transition-all';

            // Focus input
            vinInput.focus();

            // Scroll image into view
            if (items[currentIndex]) {
                items[currentIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }

            // Auto-fill VIN input if possible
            const extractedVin = extractVinFromFilename(filename);
            if (extractedVin) {
                vinInput.value = extractedVin;
            }
        }

        // Load image with selected mode
        function loadImageWithMode(filename, mode) {
            const timestamp = new Date().getTime();
            currentImage.innerHTML = `<img src="/image/${encodeURIComponent(filename)}?mode=${mode}&t=${timestamp}" alt="${filename}" class="max-w-full max-h-full object-contain">`;
        }

        // Change image mode
        function changeImageMode(mode) {
            currentImageMode = mode;

            // Update shortcut buttons
            shortcutButtons.forEach(button => {
                button.classList.remove('bg-ibm-blue-dark');
                button.classList.remove('active');

                if (button.dataset.mode === mode) {
                    button.classList.add('bg-ibm-blue-dark');
                    button.classList.add('active');
                }
            });

            // Reload current image with new mode
            if (currentIndex >= 0 && currentIndex < images.length) {
                loadImageWithMode(images[currentIndex], mode);
            }
        }

        // Go to next/prev image
        function nextImage() {
            if (currentIndex < images.length - 1) {
                selectImage(currentIndex + 1);
            }
        }

        function prevImage() {
            if (currentIndex > 0) {
                selectImage(currentIndex - 1);
            }
        }

        // Delete current image
        async function deleteImage() {
            if (currentIndex < 0 || currentIndex >= images.length) return;

            const filename = images[currentIndex];

            if (confirm(`Are you sure you want to delete ${filename}?`)) {
                try {
                    statusEl.textContent = 'Deleting...';

                    const response = await fetch('/api/delete', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ filename })
                    });

                    const data = await response.json();

                    if (data.success) {
                        // Remove from images array
                        images.splice(currentIndex, 1);

                        // Update UI
                        renderImageList();
                        statusEl.textContent = 'Ready';

                        // Select next image or previous if this was the last
                        if (images.length === 0) {
                            currentImage.innerHTML = '<div class="text-ibm-gray-50 text-center p-8">No images available</div>';
                            imageName.textContent = 'No image selected';
                            imageCount.textContent = '';
                        } else if (currentIndex >= images.length) {
                            selectImage(images.length - 1);
                        } else {
                            selectImage(currentIndex);
                        }

                        counterEl.textContent = `${processedCount} of ${images.length} processed`;
                        showMessage('Image deleted', 'success');
                    } else {
                        statusEl.textContent = 'Error';
                        showMessage(data.message, 'error');
                    }
                } catch (error) {
                    console.error('Error deleting image:', error);
                    statusEl.textContent = 'Error';
                    showMessage('Failed to delete image', 'error');
                }
            }
        }

        // Submit VIN
        async function submitVIN() {
            const vin = vinInput.value.trim().toUpperCase();
            const filename = images[currentIndex];

            // Validate VIN
            if (!vin) {
                showMessage('Please enter the last 6 characters of the VIN', 'error');
                vinInput.focus();
                return;
            }

            if (vin.length !== 6 || !(/^[A-Z0-9]{6}$/.test(vin))) {
                showMessage('VIN must be exactly 6 alphanumeric characters', 'error');
                vinInput.focus();
                return;
            }

            // Submit
            try {
                statusEl.textContent = 'Saving...';
                submitBtn.disabled = true;
                skipBtn.disabled = true;
                deleteBtn.disabled = true;

                const response = await fetch('/api/rename', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ filename, vin })
                });

                const data = await response.json();

                submitBtn.disabled = false;
                skipBtn.disabled = false;
                deleteBtn.disabled = false;

                if (data.success) {
                    processedCount++;
                    counterEl.textContent = `${processedCount} of ${images.length} processed`;

                    // Mark as processed in UI
                    const items = imageList.querySelectorAll('.image-list > div');
                    if (items[currentIndex]) {
                        items[currentIndex].classList.add('text-ibm-gray-50', 'line-through');
                    }

                    // Update VIN lists
                    if (data.vin_updated) {
                        // Reload VIN data
                        const vinResponse = await fetch('/api/vins');
                        const vinResult = await vinResponse.json();
                        vinData = vinResult;
                        renderVinList();
                        updateProgress();
                    }

                    showMessage(`Saved as VIN-B1024-${vin}${getFileExtension(filename)}`, 'success');
                    statusEl.textContent = 'Ready';

                    // Go to next image
                    if (currentIndex < images.length - 1) {
                        setTimeout(() => nextImage(), 500);
                    } else {
                        statusEl.textContent = 'All images processed';
                    }
                } else if (data.duplicate) {
                    // Handle duplicate VIN
                    statusEl.textContent = 'Duplicate VIN detected';

                    // Show comparison modal
                    showDuplicateModal(data.existing_file, filename, vin);
                } else {
                    showMessage(data.message, 'error');
                    statusEl.textContent = 'Error';
                }
            } catch (error) {
                console.error('Error submitting VIN:', error);
                showMessage('Failed to save file', 'error');
                statusEl.textContent = 'Error';
                submitBtn.disabled = false;
                skipBtn.disabled = false;
                deleteBtn.disabled = false;
            }
        }

        // Show duplicate VIN modal
        function showDuplicateModal(existingFile, newFile, vin) {
            // Set modal content
            const timestamp = new Date().getTime();
            existingImage.innerHTML = `<img src="/processed/${encodeURIComponent(existingFile)}?t=${timestamp}" alt="${existingFile}" class="max-w-full max-h-[300px] object-contain">`;
            newImage.innerHTML = `<img src="/image/${encodeURIComponent(newFile)}?t=${timestamp}" alt="${newFile}" class="max-w-full max-h-[300px] object-contain">`;

            // Show modal
            duplicateModal.classList.remove('hidden');
            duplicateModal.classList.add('flex');

            // Return a promise that resolves when user makes a choice
            return new Promise((resolve, reject) => {
                duplicateResolveCallback = resolve;

                // Handle modal buttons
                keepExisting.onclick = function() {
                    duplicateModal.classList.add('hidden');
                    duplicateModal.classList.remove('flex');
                    if (duplicateResolveCallback) {
                        duplicateResolveCallback('existing');
                        duplicateResolveCallback = null;
                    }
                };

                keepNew.onclick = function() {
                    duplicateModal.classList.add('hidden');
                    duplicateModal.classList.remove('flex');
                    if (duplicateResolveCallback) {
                        duplicateResolveCallback('new');
                        duplicateResolveCallback = null;
                    }
                };

                modalClose.onclick = modalCancel.onclick = function() {
                    duplicateModal.classList.add('hidden');
                    duplicateModal.classList.remove('flex');
                    if (duplicateResolveCallback) {
                        duplicateResolveCallback('cancel');
                        duplicateResolveCallback = null;
                    }
                };
            }).then(async (choice) => {
                if (choice === 'cancel') {
                    showMessage('Rename cancelled - please try a different VIN', 'error');
                    return;
                }

                try {
                    statusEl.textContent = 'Saving...';

                    const response = await fetch('/api/resolve-duplicate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            existing_file: existingFile,
                            new_file: newFile,
                            vin: vin,
                            choice: choice
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        showMessage(`Saved with choice: ${choice}`, 'success');
                        statusEl.textContent = 'Ready';

                        // Update VIN lists
                        const vinResponse = await fetch('/api/vins');
                        const vinResult = await vinResponse.json();
                        vinData = vinResult;
                        renderVinList();
                        updateProgress();

                        // Mark as processed in UI
                        const items = imageList.querySelectorAll('.image-list > div');
                        if (items[currentIndex]) {
                            items[currentIndex].classList.add('text-ibm-gray-50', 'line-through');
                        }

                        // Go to next image
                        if (currentIndex < images.length - 1) {
                            setTimeout(() => nextImage(), 500);
                        } else {
                            statusEl.textContent = 'All images processed';
                        }
                    } else {
                        showMessage(data.message, 'error');
                        statusEl.textContent = 'Error';
                    }
                } catch (error) {
                    console.error('Error resolving duplicate:', error);
                    showMessage('Failed to save file', 'error');
                    statusEl.textContent = 'Error';
                }
            });
        }

        // Helper functions
        function showMessage(text, type) {
            messageEl.textContent = text;
            messageEl.className = 'mt-4 h-6 transition-all';

            if (type === 'success') {
                messageEl.classList.add('text-ibm-green');
            } else if (type === 'error') {
                messageEl.classList.add('text-ibm-red');
            }
        }

        function getFileExtension(filename) {
            return filename.slice(filename.lastIndexOf('.'));
        }

        // Event listeners
        submitBtn.addEventListener('click', submitVIN);
        skipBtn.addEventListener('click', nextImage);
        deleteBtn.addEventListener('click', deleteImage);

        vinInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                submitVIN();
            }
        });

        document.addEventListener('keydown', function(e) {
            // Modal is open - handle its shortcuts
            if (!duplicateModal.classList.contains('hidden')) {
                if (e.key === 'Escape') {
                    modalClose.click();
                } else if (e.key === '1') {
                    keepExisting.click();
                } else if (e.key === '2') {
                    keepNew.click();
                }
                return;
            }

            // Regular shortcuts
            if (e.target === vinInput && e.key !== 'Tab') {
                return;  // Don't process most shortcuts when typing in the input
            }

            switch (e.key) {
                case 'ArrowRight':
                    nextImage();
                    break;
                case 'ArrowLeft':
                    prevImage();
                    break;
                case 'Delete':
                    deleteImage();
                    break;
                case '1':
                    changeImageMode('original');
                    break;
                case '2':
                    changeImageMode('bw');
                    break;
                case '3':
                    changeImageMode('contrast');
                    break;
                case '4':
                    changeImageMode('sharp');
                    break;
            }
        });

        // Format VIN input to uppercase
        vinInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });

        // Image mode buttons
        shortcutButtons.forEach(button => {
            button.addEventListener('click', function() {
                changeImageMode(this.dataset.mode);
            });
        });

        // Initial load
        loadData();
    });
    </script>
</body>
</html>"""
