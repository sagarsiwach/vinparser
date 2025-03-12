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

    // State
    let images = [];
    let currentIndex = 0;
    let processedCount = 0;
    let vinData = { vins: [], matched: [], pending: [] };
    let currentImageMode = 'original';

    // Load images and VIN data
    async function loadData() {
        try {
            statusEl.textContent = 'Loading data...';

            // Load images
            const imagesResponse = await fetch('/api/images');
            const imagesData = await imagesResponse.json();

            images = imagesData.images;
            processedCount = imagesData.processed_count || 0;

            // Update save path
            fetch('/api/config')
                .then(response => response.json())
                .then(config => {
                    savePathEl.textContent = config.processed_dir;
                });

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
                currentImage.innerHTML = '<div class="text-ibm-gray-50 text-center p-8 w-full">No images found in selected directory</div>';
                imageList.innerHTML = '<div class="p-4 text-ibm-gray-60 italic">No images found in selected directory</div>';
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

        // First sort images to show unprocessed ones first
        const sortedImages = [...images].sort((a, b) => {
            const aProcessed = isImageProcessed(a);
            const bProcessed = isImageProcessed(b);
            
            if (aProcessed && !bProcessed) return 1;
            if (!aProcessed && bProcessed) return -1;
            return a.localeCompare(b);
        });

        sortedImages.forEach((image, index) => {
            const originalIndex = images.indexOf(image);
            const item = document.createElement('div');
            item.className = 'py-3 px-4 border-b border-ibm-gray-30 cursor-pointer text-sm whitespace-nowrap overflow-hidden text-ellipsis transition-colors';

            if (originalIndex === currentIndex) {
                item.classList.add('bg-ibm-blue', 'text-white');
            }

            // Check if this image has been processed
            if (isImageProcessed(image)) {
                item.classList.add('text-ibm-gray-50');
                item.innerHTML = `<span class="inline-block w-2 h-2 rounded-full bg-ibm-green mr-2"></span>${image}`;
            } else {
                item.innerHTML = image;
            }

            item.addEventListener('click', () => selectImage(originalIndex));
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
        // Check if filename starts with "DONE_" prefix
        if (filename.startsWith('DONE_')) {
            return true;
        }
        
        // Check if VIN is in the matched list
        const vin = extractVinFromFilename(filename);
        return vin && vinData.matched.includes(vin);
    }

    // Try to extract VIN from filename
    function extractVinFromFilename(filename) {
        // Try matching our VIN format first
        const vinMatch = filename.match(/VIN[_-]([A-Z0-9]{6})/i);
        if (vinMatch) {
            return vinMatch[1].toUpperCase();
        }
            
        // Check for DONE_ prefix with VIN
        const doneMatch = filename.match(/DONE_([A-Z0-9]{6})_/i);
        if (doneMatch) {
            return doneMatch[1].toUpperCase();
        }
        
        // Try to find any 6-digit alphanumeric sequence
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

                // Update the images array with the new filename (original file has been renamed)
                if (data.raw_file_renamed) {
                    images[currentIndex] = data.raw_file_new_name;
                    renderImageList();
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

    // Expose some functions to global scope for modals
    window.appFunctions = {
        showMessage,
        nextImage,
        renderImageList,
        updateProgress,
        renderVinList,
        loadData
    };

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
        // Don't handle shortcuts if any modal is open
        if (!document.querySelector('.fixed:not(.hidden)')) {
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
                    changeImageMode('inverted');
                    break;
            }
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