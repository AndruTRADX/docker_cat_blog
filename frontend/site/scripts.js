document.addEventListener("DOMContentLoaded", async () => {
    const loadingDiv = document.getElementById("loading");
    const blogArticle = document.getElementById("blog-content");
    const titleElement = document.getElementById("blog-title");
    const contentElement = document.getElementById("blog-content-md");

    try {
        const response = await fetch("/getCatsInfo");
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.title || !data.content) {
            throw new Error("Los datos del blog no están completos");
        }
        
        titleElement.textContent = data.title;
        
        const htmlContent = marked.parse(data.content);
        contentElement.innerHTML = htmlContent;
        
        loadingDiv.classList.add("hidden");
        blogArticle.classList.remove("hidden");
        
    } catch (error) {
        console.error("Error al cargar el blog:", error);
        loadingDiv.innerHTML = `
            <div class="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-xl text-center">
                <div class="text-3xl mb-2">😿</div>
                <p class="font-bold">Oops... No se pudo cargar el blog</p>
                <p class="text-sm">${error.message}</p>
                <button onclick="location.reload()" class="mt-3 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-full transition">
                    Reintentar 🐱
                </button>
            </div>
        `;
    }
});