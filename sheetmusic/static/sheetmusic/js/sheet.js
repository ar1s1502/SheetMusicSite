import * as pdfjsLib from "https://unpkg.com/pdfjs-dist@latest/build/pdf.min.mjs";
pdfjsLib.GlobalWorkerOptions.workerSrc = "https://unpkg.com/pdfjs-dist@latest/build/pdf.worker.min.mjs";
//#TODO: add pdf full screen preview on canvas click?
//probably add some sort of error handling if pdf_bytes are not found
var pdf_bytes = JSON.parse(document.getElementById('arr-pdf').textContent);
pdf_bytes = atob(pdf_bytes);

const MAX_PREVIEW_PAGES = 3; 
const CANV_WIDTH = Math.max(window.innerWidth * 0.55, 500); //canvas should be at least 500 px wide

var pdfDoc,
    page,
    pgNum = 1,
    scale = 2.0,
    canvas = document.getElementById('sheetcanvas'),
    canvas_card = document.getElementById('canvas-card'),
    context = canvas.getContext('2d'),
    prevBtn = document.getElementById('prevPage'),
    nextBtn = document.getElementById('nextPage');

prevBtn.addEventListener('click', ()=> {
    if (pgNum <= 1) {
        return;
    }
    pgNum--;
    renderPage();
})
nextBtn.addEventListener('click', ()=> {
    if (pgNum >= MAX_PREVIEW_PAGES) {
        return;
    }
    pgNum++;
    renderPage();
})

function disableBtn(btn, bool) {
    if (bool) {
        btn.style.setProperty('visibility', 'hidden');
        btn.style.setProperty('disabled', bool + '');
    } else {    
        btn.style.setProperty('visibility', 'visible');
        btn.style.setProperty('disabled', bool + '');
    }
}

async function renderPage() {
    try {
        canvas.width = CANV_WIDTH;
        page = await pdfDoc.getPage(pgNum);
        //set scale > 1 for greater resolution render, then transform render into original desired size
        const viewport = page.getViewport({scale: scale});
        console.log(canvas.width);
        const scaledViewport = page.getViewport({scale: canvas.width / viewport.width});
        console.log("scaledViewport width: " + scaledViewport.width)
        const outputscale = (window.devicePixelRatio) || 1;
        console.log(outputscale);
        const totalscale = outputscale * scale;
        canvas.height = totalscale * scaledViewport.height;
        canvas.width =  totalscale * scaledViewport.width;

        //set displayed canvas (canvas.style dimensions) to be original intended dimensions
        //actual canvas dimensions are greater, for the sake of higher-res render.
        canvas.style.height = scale * scaledViewport.height + 'px';
        canvas.style.width = scale * scaledViewport.width + 'px';
        console.log("canvas style width: " + canvas.style.width);
        console.log("canvas style height: " + canvas.style.height);
        
        const renderContext = {
            canvasContext: context,
            viewport: scaledViewport,
            transform:[ totalscale, 0, 0, totalscale , 0, 0]
        };
        await page.render(renderContext).promise;
        console.log("canvas-card width: " + (30 + CANV_WIDTH) + 'px');
        canvas_card.style.setProperty('max-width', (Math.trunc(CANV_WIDTH + 30)) + 'px'); //+30 so card border isn't cut off
        page.cleanup();
    } 
    catch(err) {
        console.error(err);
    }
    if (pgNum == 1) {
        disableBtn(prevBtn, true);
    } else if (pgNum == MAX_PREVIEW_PAGES) {
        disableBtn(nextBtn, true);
    } else {
        disableBtn(prevBtn, false);
        disableBtn(nextBtn, false);
    }


}

async function loadPDF(pdf_bytes) {
    try{
        const loadingTask = pdfjsLib.getDocument({data: pdf_bytes});
        pdfDoc = await loadingTask.promise;
        renderPage();
    } 
    catch(err) {
        console.error(err);
    }
    if (pdfDoc.numPages <= MAX_PREVIEW_PAGES) {
        // disable and hide previous, next buttons
        disableBtn(prevBtn, true);
        disableBtn(nextBtn, true);
    } 
}

loadPDF(pdf_bytes);

