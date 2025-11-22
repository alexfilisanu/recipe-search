async function searchRecipes() {
  const query = document.getElementById("search-input").value;
  const params = new URLSearchParams({q: query});

  ["vegetarian", "vegan", "keto", "dairy_free", "gluten_free", "egg_free", "nut_free"]
      .forEach(f => {
        if (document.getElementById(f).checked) {
          params.append(f, "true");
        }
      });

  const response = await fetch(`/recipes?${params.toString()}`);
  const recipes = await response.json();
  const results = document.getElementById("results");
  results.innerHTML = "";
  if (recipes.length === 0) {
    results.innerHTML = "<li>No recipes found.</li>";
    return;
  }

  recipes.forEach(r => {
    const li = document.createElement("li");
    const highlightedTitle = (r._highlight?.title?.[0] || r.title)
        .replace(/<em>/g, "<span class='hl'>")
        .replace(/<\/em>/g, "</span>");
    const highlightIngredients = r._highlight?.["ingredients.ingredient"]?.[0] || "";
    const highlightWords = highlightIngredients.match(/<em>(.*?)<\/em>/g)
        ?.map(tag => tag.replace(/<[^>]+>/g, "").toLowerCase()) || [];

    const highlightedIngredients = r.ingredients.map(ing => {
      const words = ing.ingredient.split(/\s+/);
      const highlightedWords = words.map(w =>
          highlightWords.includes(w.toLowerCase()) ? `<span class="hl">${w}</span>` : w
      );
      return highlightedWords.join(" ");
    });
    li.innerHTML = `
      <strong>${highlightedTitle}</strong><br>
      <small>${highlightedIngredients.join(", ")}</small>
    `;

    results.appendChild(li);
  });
}
