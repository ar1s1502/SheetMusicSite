import * as pdfjsLib from "https://unpkg.com/pdfjs-dist@latest/build/pdf.min.mjs";
pdfjsLib.GlobalWorkerOptions.workerSrc = "https://unpkg.com/pdfjs-dist@latest/build/pdf.worker.min.mjs";

const pdf_dict = JSON.parse(document.getElementById("arr-data").textContent);

async function loadPDF(id, pdf_bytes) {
    try {
        const decoded_bytes = atob(pdf_bytes);
        const loadingTask = pdfjsLib.getDocument({data: decoded_bytes});
        const pdf = await loadingTask.promise;
        console.log("pdf of id " + id + " loaded")

        const pgnum = 1;
        const firstpage = await pdf.getPage(pgnum);

        //configuring html canvas to display firstpage
        const scale = 0.75;
        const viewport = firstpage.getViewport({
            scale: scale, 
        })
        const outputScale = window.devicePixelRatio || 1;

        const canvas_id = 'canvas-'+id;
        const canvas = document.getElementById(canvas_id);
        const context = canvas.getContext('2d');
        canvas.height = Math.floor(outputScale * viewport.height / 2);
        canvas.width = Math.floor(outputScale * viewport.width );
        //displayed dimension still original scaled viewport dimension
        canvas.style.height = ( viewport.height/2) + 'px';
        canvas.style.width = ( viewport.width) + 'px';

        const renderContext = {
            canvasContext: context,
            viewport: viewport,
            transform: [outputScale, 0, 0, outputScale, 0, 0]
        }
        await firstpage.render(renderContext).promise;
        console.log('rendered');
        firstpage.cleanup();
    }
    catch(err) {
        console.error(err);
    }
}

for (const [id, pdf_bytes] of Object.entries(pdf_dict)) {
    loadPDF(id, pdf_bytes)
}





