// Cropper.js برای کراپ کردن تصاویر
// این فایل شامل کدهای JavaScript برای interface کراپ است

document.addEventListener('DOMContentLoaded', function() {
    // تنظیمات cropper
    const cropperOptions = {
        aspectRatio: 4/3, // نسبت ابعاد ثابت (می‌توانید تغییر دهید)
        viewMode: 1,
        dragMode: 'move',
        autoCropArea: 0.8,
        restore: false,
        guides: true,
        center: true,
        highlight: false,
        cropBoxMovable: true,
        cropBoxResizable: true,
        toggleDragModeOnDblclick: false,
        background: false,
        modal: true,
        responsive: true,
        checkCrossOrigin: false,
        checkOrientation: false,
        scalable: false,
        zoomable: false,
        rotatable: false,
        minCropBoxWidth: 200,
        minCropBoxHeight: 150,
        maxCropBoxWidth: 800,
        maxCropBoxHeight: 600
    };

    // تابع شروع cropper
    function initCropper(imageElement, options = {}) {
        const finalOptions = { ...cropperOptions, ...options };
        return new Cropper(imageElement, finalOptions);
    }

    // تابع کراپ و ذخیره
    function cropAndSave(cropper, targetSize = {width: 800, height: 600}) {
        const canvas = cropper.getCroppedCanvas({
            width: targetSize.width,
            height: targetSize.height,
            imageSmoothingEnabled: true,
            imageSmoothingQuality: 'high'
        });
        
        return canvas.toDataURL('image/jpeg', 0.9);
    }

    // تابع نمایش modal کراپ
    function showCropModal(imageSrc, targetSize = {width: 800, height: 600}, callback) {
        // ایجاد modal HTML
        const modalHtml = `
            <div class="crop-modal" id="cropModal" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.8);
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                direction: rtl;
            ">
                <div class="crop-container" style="
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    max-width: 90%;
                    max-height: 90%;
                    position: relative;
                ">
                    <div class="crop-header" style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 20px;
                        border-bottom: 1px solid #eee;
                        padding-bottom: 15px;
                    ">
                        <h4 style="margin: 0; color: #333;">کراپ تصویر</h4>
                        <button type="button" class="close-crop" style="
                            background: none;
                            border: none;
                            font-size: 24px;
                            cursor: pointer;
                            color: #999;
                        ">&times;</button>
                    </div>
                    
                    <div class="crop-preview" style="
                        max-width: 100%;
                        max-height: 60vh;
                        overflow: hidden;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                    ">
                        <img id="cropImage" src="${imageSrc}" style="
                            max-width: 100%;
                            max-height: 100%;
                            display: block;
                        ">
                    </div>
                    
                    <div class="crop-controls" style="
                        margin-top: 20px;
                        display: flex;
                        gap: 10px;
                        justify-content: center;
                    ">
                        <button type="button" class="btn btn-primary" id="cropConfirm">
                            <i class="fas fa-check"></i> تایید کراپ
                        </button>
                        <button type="button" class="btn btn-secondary" id="cropCancel">
                            <i class="fas fa-times"></i> انصراف
                        </button>
                    </div>
                    
                    <div class="crop-info" style="
                        margin-top: 15px;
                        text-align: center;
                        color: #666;
                        font-size: 14px;
                    ">
                        اندازه نهایی: ${targetSize.width} × ${targetSize.height} پیکسل
                    </div>
                </div>
            </div>
        `;

        // اضافه کردن modal به صفحه
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        const modal = document.getElementById('cropModal');
        const cropImage = document.getElementById('cropImage');
        const confirmBtn = document.getElementById('cropConfirm');
        const cancelBtn = document.getElementById('cropCancel');
        const closeBtn = document.querySelector('.close-crop');

        // تنظیم aspect ratio بر اساس target size
        const aspectRatio = targetSize.width / targetSize.height;
        const cropper = initCropper(cropImage, { aspectRatio });

        // رویدادهای modal
        function closeModal() {
            cropper.destroy();
            modal.remove();
        }

        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        
        // کلیک خارج از modal
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });

        // تایید کراپ
        confirmBtn.addEventListener('click', function() {
            const croppedDataUrl = cropAndSave(cropper, targetSize);
            callback(croppedDataUrl);
            closeModal();
        });

        // ESC برای بستن
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
    }

    // تابع اصلی برای شروع کراپ
    window.startImageCrop = function(imageSrc, targetSize = {width: 800, height: 600}, callback) {
        showCropModal(imageSrc, targetSize, callback);
    };

    // تابع برای فرم‌های Django
    window.setupCropButton = function(inputId, previewId, targetSize = {width: 800, height: 600}) {
        const fileInput = document.getElementById(inputId);
        const preview = document.getElementById(previewId);
        
        if (fileInput && preview) {
            fileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                        
                        // اضافه کردن دکمه کراپ
                        let cropBtn = document.getElementById('cropBtn');
                        if (!cropBtn) {
                            cropBtn = document.createElement('button');
                            cropBtn.id = 'cropBtn';
                            cropBtn.type = 'button';
                            cropBtn.className = 'btn btn-info mt-2';
                            cropBtn.innerHTML = '<i class="fas fa-crop"></i> کراپ تصویر';
                            preview.parentNode.appendChild(cropBtn);
                        }
                        
                        cropBtn.onclick = function() {
                            startImageCrop(e.target.result, targetSize, function(croppedDataUrl) {
                                // تبدیل data URL به blob و تنظیم در input
                                fetch(croppedDataUrl)
                                    .then(res => res.blob())
                                    .then(blob => {
                                        const file = new File([blob], 'cropped-image.jpg', {type: 'image/jpeg'});
                                        const dataTransfer = new DataTransfer();
                                        dataTransfer.items.add(file);
                                        fileInput.files = dataTransfer.files;
                                        
                                        // به‌روزرسانی preview
                                        preview.src = croppedDataUrl;
                                    });
                            });
                        };
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    };
});
