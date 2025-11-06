const API_URL = "http://localhost:8000";

// Função para lidar com o upload de imagens
async function handleUpload() {
  const file = document.getElementById("uploadFile").files[0];
  if (!file) return alert("Selecione um arquivo!");

  const formData = new FormData();
  formData.append("imagem", file);

  try {
    const res = await fetch(`${API_URL}/upload`, {
      method: "POST",
      body: formData
    });
    
    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Erro desconhecido no upload");
    }
    
    const data = await res.json();
    alert(data.mensagem || "Upload concluido!");
  } catch (err) {
    alert("Erro no upload: " + err.message);
  }
}

// Função para lidar com a busca de imagens similares
async function handleSearch() {
  const file = document.getElementById("searchFile").files[0];
  if (!file) return alert("Selecione um arquivo!");

  const threshold = parseFloat(document.getElementById("thresholdInput").value);
  if (threshold < 0.0 || threshold > 1.0) return alert("Threshold deve estar entre 0.0 e 1.0");

  const formData = new FormData();
  formData.append("imagem", file);
  formData.append("threshold", threshold);

  try {
    const res = await fetch(`${API_URL}/search`, {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Erro desconhecido na busca");
    }

    const data = await res.json();
    renderResults(data.similar_faces || []);
  } catch (err) {
    alert("Erro na busca: " + err.message);
  }
}

// Função para renderizar os resultados na página
function renderResults(results) {
  const container = document.getElementById("results");
  container.innerHTML = "";

  if (results.length === 0) {
    container.innerHTML = "<p>Nenhum resultado encontrado.</p>";
    return;
  }

  results.forEach(r => {
    const div = document.createElement("div");
    div.className = "result";
    const imgPath = r.img_path.replace("./db/DATASET", "/db/DATASET");

    div.innerHTML = `
      <img src="${imgPath}" alt="face"/>
      <p><strong>ID:</strong> ${r.id}</p>
      <p><strong>Arquivo:</strong> ${r.img_path}</p>
      <p><strong>Similaridade:</strong> ${r.similarity.toFixed(2)}</p>
    `;
    container.appendChild(div);
  });
}