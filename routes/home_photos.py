from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request
from routes.auth import get_current_user

router = APIRouter()


@router.get('/gallery', response_class=HTMLResponse)
async def photos(request: Request):
    if await get_current_user(request) is None:
        return RedirectResponse(url="/login")

    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Photo Gallery</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --bg: #0b0f14;
            --panel: #111821;
            --panel-soft: #151e28;
            --border: #233041;
            --text: #edf3f8;
            --muted: #8fa0b3;
            --accent: #7dd3fc;
            --accent-soft: rgba(125, 211, 252, 0.12);
            --green: #4ade80;
        }
        body {
            min-height: 100vh;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                         BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: radial-gradient(circle at top, rgba(37, 99, 235, .08), transparent 35%), var(--bg);
            color: var(--text);
            line-height: 1.6;
        }
        header {
            padding: 22px max(24px, calc((100vw - 1120px) / 2));
            border-bottom: 1px solid var(--border);
            background: rgba(11, 15, 20, .88);
            backdrop-filter: blur(16px);
        }
        .brand { display: flex; align-items: center; gap: 12px; }
        .logo {
            width: 40px; height: 40px; display: grid; place-items: center;
            background: var(--accent-soft); border: 1px solid rgba(125, 211, 252, .22);
            border-radius: 11px; font-size: 20px;
        }
        .brand strong { font-size: 15px; letter-spacing: .02em; }
        .brand span { display: block; font-size: 12px; color: var(--muted); }
        main { max-width: 1120px; margin: 0 auto; padding: 54px 24px 100px; }
        .eyebrow {
            font-size: 12px; letter-spacing: .13em; text-transform: uppercase;
            font-weight: 700; color: var(--accent); margin-bottom: 12px;
        }
        h1 { font-size: clamp(38px, 5vw, 60px); line-height: 1.08; letter-spacing: -.04em; }
        .intro { color: var(--muted); font-size: 16px; margin-top: 14px; margin-bottom: 32px; }
        .upload {
            display: block; text-align: center; cursor: pointer;
            padding: 42px 24px; border: 1px dashed #36506b;
            border-radius: 16px;
            background: linear-gradient(180deg, rgba(17, 24, 33, .96), rgba(13, 19, 26, .96));
            box-shadow: 0 16px 40px rgba(0,0,0,.15);
            transition: background .2s, border-color .2s, transform .2s;
            animation: fadeDown 0.35s ease-out;

        }
        .upload:hover, .upload.dragging {
            border-color: var(--accent); background: #172433; transform: translateY(-1px);
        }
        .upload-icon {
            width: 48px; height: 48px; display: grid; place-items: center;
            margin: 0 auto 17px; border-radius: 16px;
            border: 1px solid rgba(125,211,252,.22); background: var(--accent-soft);
            font-size: 28px;
        }
        .upload h2 { font-size: 21px; letter-spacing: -.02em; }
        .upload p { color: var(--muted); margin-top: 5px; font-size: 14px; }
        .formats {
            display: inline-block; margin-top: 20px; padding: 7px 12px;
            border-radius: 999px; border: 1px solid var(--border);
            color: #bcc8d4; background: var(--panel-soft);
            font-size: 12px; font-weight: 600;
        }
        #status { min-height: 24px; margin-top: 15px; font-size: 14px; color: var(--accent); }
        .section-heading {
            display: flex; justify-content: space-between; align-items: baseline;
            gap: 16px;
        }
        .section-heading h2 {
            font-size: 23px;
            letter-spacing: -.02em;
        }
        #photoCount { font-size: 13px; color: var(--muted); }
        .grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
            gap: 18px; margin-top: 20px;
        }
        .card {
            position: relative;
            overflow: hidden; border-radius: 14px; cursor: pointer;
            border: 1px solid var(--border);
            background: linear-gradient(180deg, rgba(17,24,33,.95), rgba(13,19,26,.95));
            box-shadow: 0 16px 40px rgba(0,0,0,.14);
            transition: border-color .18s, transform .18s, box-shadow .18s;
            animation: fadeUpScale 0.35s ease-out;
        }
        .card:hover {
            border-color: #36506b; transform: scale(1.2);
            box-shadow: 0 18px 42px rgba(0,0,0,.3);
        }
        .preview {
            height: 160px;
            background: var(--panel-soft);
            display: grid;
            place-items: center;
        }
        .preview img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .filename {
            padding: 13px 14px; font-size: 13px; font-weight: 500;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .delete-button {
            position: absolute;
            right: 10px;
            bottom: 10px;
            width: 34px;
            height: 34px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: none;
            border-radius: 8px;
            background: #f77070;
            color: white;
            cursor: pointer;
            z-index: 2;
            opacity: 0;
            transform: translateY(4px);
            transition: opacity .2s, transform .2s, background .2s;
        }
        .card:hover .delete-button,
        .card:focus-within .delete-button {
            opacity: 1;
            transform: translateY(0);
        }
        .delete-button:hover { background: #e05252; }
        .delete-button:disabled { opacity: .6; cursor: wait; }
        .delete-button svg { pointer-events: none; }
        @media (hover: none) {
            .delete-button { opacity: 1; transform: none; }
        }
        .empty { grid-column: 1 / -1; color: var(--muted); font-size: 14px; padding: 22px 0; }
        @media (max-width: 600px) {
            main { padding: 38px 20px 70px; }
            header { padding: 18px 20px; }
            .upload { padding: 40px 18px; }
            .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
            .preview { height: 135px; }
        }
        .nav-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 150px;
            padding: 10px 16px;
            border: 1px solid var(--border);
            border-radius: 10px;
            background: var(--panel-soft);
            color: var(--text);
            font-size: 16px;
            font-weight: 600;
            text-decoration: none;
            white-space: nowrap;
            transition: background .2s, border-color .2s, transform .2s;
        }
        .nav-button:hover {
            background: var(--accent-soft);
            border-color: var(--accent);
            transform: translateY(-1px);
        }
        .nav-button:focus-visible {
            outline: 2px solid var(--accent);
            outline-offset: 3px;
        }
        .show-more-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 14px 22px;
            border: 1px solid var(--border);
            border-radius: 10px;
            background: var(--panel-soft);
            color: var(--text);
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            text-decoration: none;
            white-space: nowrap;
            transition: background .2s, border-color .2s, transform .2s;
        }
        .show-more-button:hover {
            background: var(--accent-soft);
            border-color: var(--accent);
            transform: translateY(-1px);
        }
        .show-more-button:focus-visible {
            outline: 2px solid var(--accent);
            outline-offset: 3px;
        }
        .show-more-container {
            width: fit-content;
            padding: 24px;
            margin: 0 auto;
            border-radius: 14px;
            cursor: pointer;
            transition: border-color .18s, transform .18s, box-shadow .18s;
        }
        .eyebrow-container {
            animation: fadeDown 0.35s ease-out;
        }

        @keyframes fadeDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        @keyframes fadeUpScale {
            from {
                opacity: 0;
                scale: 0;
                transform: translateY(15px);
            }
            to {
                opacity: 1;
                scale: 1;
                transform: translateY(0);
            }
        }
        .delete-dialog {
            position: fixed;
            inset: 0;
            margin: auto;
            width: min(400px, calc(100% - 32px));
            padding: 30px;
            background: #111821;
            color: #edf3f8;
            border: 1px solid #233041;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 24px 80px rgba(0, 0, 0, .5);
            animation: fadeDown 0.35s ease-out;
        }

        .delete-dialog::backdrop {
            background: rgba(0, 0, 0, .7);
            backdrop-filter: blur(5px);
        }

        .dialog-icon {
            font-size: 32px;
            margin-bottom: 16px;
        }

        .delete-dialog h2 {
            font-size: 22px;
            margin-bottom: 10px;
        }

        .delete-dialog p {
            color: #8fa0b3;
            font-size: 14px;
            overflow-wrap: anywhere;
            margin-bottom: 26px;
        }

        .dialog-actions {
            display: flex;
            gap: 12px;
        }

        .dialog-actions button {
            flex: 1;
            padding: 12px;
            border-radius: 9px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
        }

        .dialog-cancel {
            background: #151e28;
            color: white;
            border: 1px solid #233041;
        }

        .dialog-confirm {
            background: #f77070;
            color: white;
            border: none;
        }
        .delete-preview {
            display: block;
            width: 100%;
            max-height: 220px;
            object-fit: contain;
            border-radius: 10px;
            margin-bottom: 24px;
            background: #0b0f14;
        }
        .dialog-confirm:hover {
            background: #e05252;
        }

        /* Full-resolution photo viewer */
        .photo-dialog {
            position: fixed;
            inset: 0;
            margin: auto;
            padding: 16px;
            width: max-content;
            max-width: 95vw;
            max-height: 95vh;
            overflow: auto;
            background: var(--panel);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: 0 24px 80px rgba(0, 0, 0, .65);
            animation: fadeDown 0.35s ease-out;
        }
        .photo-dialog::backdrop {
            background: rgba(0, 0, 0, .85);
            backdrop-filter: blur(8px);
        }
        .photo-dialog-image {
            display: block;
            max-width: calc(95vw - 34px);
            max-height: calc(95vh - 100px);
            width: auto;
            height: auto;
            object-fit: contain;
            border-radius: 8px;
        }
        .photo-dialog-name {
            max-width: calc(95vw - 34px);
            margin-top: 12px;
            text-align: center;
            font-size: 24px;
            color: var(--muted);
            overflow-wrap: anywhere;
        }
        .photo-dialog-close {
            position: absolute;
            top: 24px;
            right: 24px;
            z-index: 3;
            width: 36px;
            height: 36px;
            border: none;
            border-radius: 9px;
            background: rgba(11, 15, 20, .85);
            color: white;
            font-size: 26px;
            line-height: 1;
            cursor: pointer;
        }
        .photo-dialog-close:hover { background: #f77070; }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <a class="nav-button" href="/">🏠 Home</a>
            <a class="nav-button" href="/gallery">📸 Photos</a>
            <a class="nav-button" href="/clips">📹 Clips</a>
            <a class="nav-button" href="/documentation">🗿 Docs</a>
            <a class="nav-button"
                onclick="logout(event)"
                style="width: 110px; margin-left: auto; color: #f87171; border-color: rgba(248, 113, 113, 0.25); cursor: pointer;">
                Logout
            </a>
            <a class="nav-button"
                href="/account"
                style="width: 110px; color: rgba(255, 255, 255); border-color: rgba(255, 255, 255, 0.25); cursor: pointer;">
                ⚙️ Account
            </a>
        </div>
    </header>
    <main>
        <div class="eyebrow-container">
            <div class="eyebrow" id="eyebrow"></div>
            <h1>Every photo, one place.</h1>
            <p class="intro">Upload, browse, and revisit your favourite moments.</p>
        </div>

        <div class="upload" id="dropzone" role="button" tabindex="0" aria-label="Upload photos">
            <div class="upload-icon">📸️</div>
            <h2>Drop your photos here</h2>
            <p>Or click to browse your computer</p>
            <span class="formats">PNG · JPG · JPEG</span>
            <input type="file" id="fileInput" accept=".png,.jpg,.jpeg,image/png,image/jpeg" multiple hidden>
        </div>
        <div id="status" role="status" aria-live="polite"></div>

        <div class="section-heading">
            <h2>My Photos</h2>
            <span id="photoCount"></span>
        </div>
        <div class="grid" id="fileGrid"></div>
        <div id="show-more" class="show-more-container">
            <button class=show-more-button onClick=loadPhotos()>Show more</button>
        </div>
    </main>
    <script>
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        const grid = document.getElementById('fileGrid');
        const status = document.getElementById('status');
        const photoCount = document.getElementById('photoCount');

        dropzone.onclick = () => fileInput.click();
        dropzone.onkeydown = (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                fileInput.click();
            }
        };
        fileInput.onchange = async () => {
            await uploadPhotos(fileInput.files);
            fileInput.value = '';
        };
        dropzone.ondragover = (event) => {
            event.preventDefault();
            dropzone.classList.add('dragging');
        };
        dropzone.ondragleave = () => dropzone.classList.remove('dragging');
        dropzone.ondrop = async (event) => {
            event.preventDefault();
            dropzone.classList.remove('dragging');
            await uploadPhotos(event.dataTransfer.files);
        };

        const visibleCount = 15;
        let files = [];
        let displayed = 0;

        async function getFiles() {
            const response = await fetch('/api/photos');
            if (!response.ok) throw new Error('Could not load photos');
                    files = await response.json();
        }

        async function uploadPhotos(files) {
            for (const file of files) {
                const extension = file.name.split('.').pop().toLowerCase();
                if (!['png', 'jpg', 'jpeg'].includes(extension)) {
                    status.textContent = '❌ Unsupported photo format: ' + file.name;
                    return;
                }
                const data = new FormData();
                data.append('file', file);
                status.textContent = 'Uploading ' + file.name + '...';
                try {
                    const response = await fetch('/api/file', { 
                        method: 'POST',
                        body: data
                    });

                    if (!response.ok) {
                        const error = await response.json().catch(() => ({}));
                        throw new Error('Upload failed: ' + (error.detail || response.statusText));
                    }
                } catch (error) {
                    status.textContent = error.message;
                    return;
                }
            }
            status.textContent = '✅ Photos uploaded successfully!';
            await getFiles();
            displayed = 0;
            grid.replaceChildren();
            await loadPhotos();
        }

        async function loadUsername() {
            const response = await fetch("/api/users/me");
            const data = await response.json();

            console.log(data);

            document.getElementById("eyebrow").textContent = `${data.user.username}'s Photos`;
        }
        loadUsername();

        function updateGalleryUI() {
            photoCount.textContent = displayed + (displayed === 1 ? ' photo' : ' photos');
            const showMore = document.getElementById('show-more');
            if (showMore) showMore.style.display = displayed < files.length ? '' : 'none';

            grid.querySelectorAll('.empty').forEach(element => element.remove());
            if (files.length === 0) {
                const empty = document.createElement('p');
                empty.className = 'empty';
                empty.textContent = '📷 No photos uploaded yet.';
                grid.appendChild(empty);
            }
        }

        async function loadPhotos() {
            try {
                if (files.length === 0 && displayed === 0) {
                    await getFiles();
                }

                for (const photo of files.slice(displayed, displayed + visibleCount)) {
                    await new Promise(resolve => setTimeout(resolve, 100));

                    const name = typeof photo === 'string' ? photo : photo.storage_name;
                    if (typeof name !== 'string') continue;
                    const displayName = typeof photo === 'string' ? photo : (photo.filename || name);
                    const thumb_url = `/api/file/${encodeURIComponent(name)}?size=thumbnail`;
                    const original_url = `/api/file/${encodeURIComponent(name)}`;

                    const card = document.createElement('div');
                    card.className = 'card';
                    card.tabIndex = 0;
                    card.setAttribute('role', 'link');
                    card.setAttribute('aria-label', `Open ${displayName}`);

                    const preview = document.createElement('div');
                    preview.className = 'preview';
                    const img = document.createElement('img');
                    img.src = thumb_url;
                    img.alt = displayName;
                    img.loading = 'lazy';
                    preview.appendChild(img);

                    const label = document.createElement('div');
                    label.className = 'filename';
                    label.textContent = displayName;
                    label.title = displayName;
                    card.append(preview, label);

                    const deleteButton = document.createElement('button');
                    deleteButton.type = 'button';
                    deleteButton.className = 'delete-button';
                    deleteButton.title = 'Delete photo';
                    deleteButton.setAttribute('aria-label', `Delete ${displayName}`);
                    deleteButton.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                             viewBox="0 0 24 24" fill="none" stroke="white"
                             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M3 6h18"/>
                            <path d="M8 6V4h8v2"/>
                            <path d="M19 6l-1 14H6L5 6"/>
                            <path d="M10 11v6"/>
                            <path d="M14 11v6"/>
                        </svg>`;

                    deleteButton.onclick = async (event) => {
                        event.stopPropagation();

                        const confirmed = await confirmDeletePhoto(displayName, name);
                        if (!confirmed) return;

                        deleteButton.disabled = true;

                        try {
                            const response = await fetch(
                                `/api/file/${encodeURIComponent(name)}`,
                                {
                                    method: 'DELETE',
                                    credentials: 'same-origin'
                                }
                            );

                            if (!response.ok) {
                                const error = await response.json().catch(() => ({}));

                                throw new Error(
                                    typeof error.detail === 'string'
                                        ? error.detail
                                        : `Delete failed (${response.status})`
                                );
                            }

                            const index = files.findIndex(item =>
                                (typeof item === 'string' ? item : item.storage_name) === name
                            );

                            if (index !== -1) files.splice(index, 1);

                            card.remove();
                            displayed = Math.max(0, displayed - 1);

                            updateGalleryUI();

                            status.textContent = `Deleted ${displayName}`;

                        } catch (error) {
                            status.textContent = error.message;
                            deleteButton.disabled = false;
                        }
                    };
                    deleteButton.onkeydown = event => event.stopPropagation();
                    card.appendChild(deleteButton);

                    const openPhoto = () => openPhotoDialog(original_url, displayName);
                    card.onclick = openPhoto;
                    card.onkeydown = (event) => {
                        if (event.target === card && event.key === 'Enter') openPhoto();
                    };
                    grid.appendChild(card);
                    displayed++;
                }
                updateGalleryUI();
            } catch (error) {
                status.textContent = error.message;
            }
        }

        async function logout(event) {
            event.preventDefault();

            try {
                const response = await fetch('/api/auth/logout', {
                    method: 'POST'
                });

                if (!response.ok) {
                    throw new Error('Logout failed');
                }

                window.location.href = '/login';

            } catch (error) {
                console.error(error);
            }
        }
        function openPhotoDialog(imageUrl, displayName) {
            const dialog = document.getElementById('photoDialog');
            const image = document.getElementById('photoDialogImage');
            const filename = document.getElementById('photoDialogName');

            image.src = imageUrl;
            image.alt = displayName;
            filename.textContent = displayName;
            dialog.showModal();
        }

        function confirmDeletePhoto(displayName, storageName) {
            return new Promise(resolve => {
                const dialog = document.getElementById('deleteDialog');
                const message = document.getElementById('deleteMessage');
                const confirmButton = document.getElementById('confirmDelete');
                const cancelButton = document.getElementById('cancelDelete');

                const preview = document.getElementById('deletePreview');
                preview.src = `/api/file/${encodeURIComponent(storageName)}?size=thumbnail`;

                message.textContent = `Permanently delete "${displayName}"? This cannot be undone.`;

                const cleanup = () => {
                    confirmButton.removeEventListener('click', onConfirm);
                    cancelButton.removeEventListener('click', onCancel);
                    dialog.removeEventListener('cancel', onCancel);
                    dialog.removeEventListener('close', onClose);
                };

                const finish = result => {
                    cleanup();
                    dialog.close();
                    resolve(result);
                };

                const onConfirm = () => finish(true);
                const onCancel = event => {
                    event?.preventDefault();
                    finish(false);
                };

                const onClose = () => {
                    cleanup();
                    resolve(false);
                };

                confirmButton.addEventListener('click', onConfirm);
                cancelButton.addEventListener('click', onCancel);
                dialog.addEventListener('cancel', onCancel);
                dialog.addEventListener('close', onClose);

                dialog.showModal();
            });
        }

        loadPhotos();
    </script>

    <dialog id="deleteDialog" class="delete-dialog">
        <div class="dialog-icon">🗑️</div>
        <h2>Delete photo?</h2>
        <p id="deleteMessage"></p>

        <img id="deletePreview" class="delete-preview" src="" alt="Photo preview">

        <div class="dialog-actions">
            <button id="cancelDelete" class="dialog-cancel">
                Cancel
            </button>
            <button id="confirmDelete" class="dialog-confirm">
                Delete
            </button>
        </div>
    </dialog>

    <dialog id="photoDialog" class="photo-dialog" aria-label="Photo viewer">
        <button type="button" id="closePhotoDialog" class="photo-dialog-close" aria-label="Close photo">&times;</button>
        <img id="photoDialogImage" class="photo-dialog-image" alt="Full-size photo">
        <p id="photoDialogName" class="photo-dialog-name"></p>
    </dialog>

    <script>
        const photoDialog = document.getElementById('photoDialog');
        document.getElementById('closePhotoDialog').onclick = () => photoDialog.close();

        photoDialog.addEventListener('click', event => {
            // Clicks on the backdrop land on the dialog element itself.
            if (event.target !== photoDialog) return;
            const bounds = photoDialog.getBoundingClientRect();
            const outside = event.clientX < bounds.left || event.clientX > bounds.right ||
                            event.clientY < bounds.top || event.clientY > bounds.bottom;
            if (outside) photoDialog.close();
        });

        photoDialog.addEventListener('close', () => {
            document.getElementById('photoDialogImage').removeAttribute('src');
        });
    </script>
</body>
</html>"""
