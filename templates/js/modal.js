document.addEventListener('DOMContentLoaded', function() {
    // Modal elements
    const duplicateModal = document.getElementById('duplicate-modal');
    const modalClose = document.getElementById('modal-close');
    const modalCancel = document.getElementById('modal-cancel');
    const keepExisting = document.getElementById('keep-existing');
    const keepNew = document.getElementById('keep-new');
    const existingImage = document.getElementById('existing-image');
    const newImage = document.getElementById('new-image');

    let duplicateResolveCallback = null;

    // Show duplicate VIN modal
    window.showDuplicateModal = function(existingFile, newFile, vin) {
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
                closeModal('existing');
            };

            keepNew.onclick = function() {
                closeModal('new');
            };

            modalClose.onclick = modalCancel.onclick = function() {
                closeModal('cancel');
            };
        }).then(async (choice) => {
            if (choice === 'cancel') {
                window.appFunctions.showMessage('Rename cancelled - please try a different VIN', 'error');
                return;
            }

            try {
                document.getElementById('status').textContent = 'Saving...';

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
                    window.appFunctions.showMessage(`Saved with choice: ${choice}`, 'success');
                    document.getElementById('status').textContent = 'Ready';

                    // Update VIN data and UI
                    await window.appFunctions.loadData();

                    // Go to next image
                    setTimeout(() => window.appFunctions.nextImage(), 500);
                } else {
                    window.appFunctions.showMessage(data.message, 'error');
                    document.getElementById('status').textContent = 'Error';
                }
            } catch (error) {
                console.error('Error resolving duplicate:', error);
                window.appFunctions.showMessage('Failed to save file', 'error');
                document.getElementById('status').textContent = 'Error';
            }
        });
    }

    function closeModal(result) {
        duplicateModal.classList.add('hidden');
        duplicateModal.classList.remove('flex');
        if (duplicateResolveCallback) {
            duplicateResolveCallback(result);
            duplicateResolveCallback = null;
        }
    }

    // Keyboard shortcuts for modal
    document.addEventListener('keydown', function(e) {
        if (!duplicateModal.classList.contains('hidden')) {
            if (e.key === 'Escape') {
                modalClose.click();
            } else if (e.key === '1') {
                keepExisting.click();
            } else if (e.key === '2') {
                keepNew.click();
            }
        }
    });
});