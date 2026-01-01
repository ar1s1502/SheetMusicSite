import * as pdfjsLib from "https://unpkg.com/pdfjs-dist@latest/build/pdf.min.mjs";
pdfjsLib.GlobalWorkerOptions.workerSrc = "https://unpkg.com/pdfjs-dist@latest/build/pdf.worker.min.mjs";
//#TODO: add pdf full screen preview on canvas click?
//probably add some sort of error handling if pdf_bytes are not found
var pdf_bytes = JSON.parse(document.getElementById('arr-data').textContent);
pdf_bytes = atob(pdf_bytes);

const MAX_PREVIEW_PAGES = 3; 

var pdfDoc,
    page,
    pgNum = 1,
    scale = 1.5,
    canvas = document.getElementById('sheetcanvas'),
    context = canvas.getContext('2d');

document.getElementById('prevPage').addEventListener('click', ()=> {
    if (pgNum <= 1) {
        return;
    }
    pgNum--;
    renderPage()
})
document.getElementById('nextPage').addEventListener('click', ()=> {
    if (pgNum >= MAX_PREVIEW_PAGES) {
        return;
    }
    pgNum++;
    renderPage();
})

async function renderPage() {
    try {
        page = await pdfDoc.getPage(pgNum);
        const viewport = page.getViewport({scale: scale});
        const outputscale = (0.75 * window.devicePixelRatio) || 1;
        console.log(outputscale);
        canvas.height = 0.8 * viewport.height;
        canvas.width = viewport.width;
        // canvas.style.height = 500 + 'px';
        // canvas.style.width = 300 + 'px';
        // canvas.height = 500 + 'px';
        // // canvas.height = Math.floor(outputscale * viewport.height);
        // canvas.style.height = 500  + 'px';
        // canvas.width = Math.floor(outputscale * viewport.width);
        // canvas.style.width = 500+ 'px';

        const renderContext = {
            canvasContext: context,
            viewport: viewport,
            // transform:[1, 0, 0, 1, 0, 0]
        };
        await page.render(renderContext).promise;
        console.log('rendered');
        page.cleanup();
    } 
    catch(err) {
        console.error(err);
    }
}

async function loadPDF(pdf_bytes) {
    try{
        const loadingTask = pdfjsLib.getDocument({data: pdf_bytes});
        pdfDoc = await loadingTask.promise;
        renderPage();
        if (pdfDoc.numPages <= MAX_PREVIEW_PAGES) {
            // disable + hide previous, next buttons
        } 
    } 
    catch(err) {
        console.error(err);
    }
}

loadPDF(pdf_bytes);

