
const DATA = window.YU_KAOYAN_DATA;
const app = document.getElementById("app");
const storageKey = "yu-kaoyan-checklist-v1";
const checklistFormat = "yu-kaoyan-checklist";
let expanded = new Set();

const esc = (value = "") => String(value).replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const regexEscape = (value) => value.replace(/[.*+?^\${}()|[\]\\]/g, "\\$&");
const highlight = (value, query) => {
  const text = esc(value);
  const term = query?.trim();
  if (!term) return text;
  return text.replace(new RegExp("(" + regexEscape(esc(term)) + ")", "ig"), "<mark>$1</mark>");
};
const nav = (route, label, className = "") => '<a class="' + className + '" href="#' + route + '">' + label + '</a>';
const trackLabel = (track) => track === "math" ? "数学一" : "408";

function parseRoute() {
  const raw = location.hash.slice(1) || "home";
  const [path, query = ""] = raw.split("?");
  return { path, params: new URLSearchParams(query) };
}

function subjectGroup(eyebrow, title, description, items) {
  return '<section class="subject-group"><header><p class="section-kicker">' + eyebrow + '</p><h2>' + title + '</h2><p>' + description + '</p></header><div class="subject-grid">' + items.map((subject, index) =>
    '<a class="subject-card" href="#subject/' + subject.slug + '"><div class="subject-index">' + String(index + 1).padStart(2, "0") + '</div><div><h3>' + subject.name + '</h3><p>' + subject.description + '</p></div><footer><span>' + subject.chapters.length + ' 章</span><strong>' + (subject.slug === "gaoshu" ? "第一章样板已完成" : "目录已建立") + '</strong><span aria-hidden="true">→</span></footer></a>'
  ).join("") + '</div></section>';
}

function renderHome() {
  const math = DATA.subjects.filter((item) => item.track === "math");
  const cs = DATA.subjects.filter((item) => item.track === "408");
  return '<main><section class="home-hero page-wrap"><div class="hero-copy"><p class="hero-overline">个人考研知识库 · 2027 备考</p><h1>把数学一与 408，<br>整理成一套随时能翻开的教材。</h1><p>面向手机、平板与电脑的完整复习库。每章按“基础精讲＋强化提高”组织，只保留知识、公式、方法与易错点，不放例题、题库和进度仪表盘。</p><div class="hero-actions">' + nav("chapter/gaoshu-1", "阅读高数第一章样板", "primary-button") + nav("search", "搜索全站知识", "secondary-button") + '</div></div><aside class="hero-note"><span>阶段一</span><strong>框架已就位</strong><p>七科目录、搜索、章节模板、本地清单和多端布局均可验收；正式内容仅开放高数第一章。</p>' + nav("scope", "查看资料与考纲校准 →") + '</aside></section><div class="home-content page-wrap">' + subjectGroup("301 · 数学一", "数学一", "高等数学建立分析工具，线性代数处理线性结构，概率论描述随机规律。", math) + subjectGroup("408 · 计算机学科专业基础", "408", "从数据结构到计算机系统，再到操作系统与网络，建立贯通软硬件的系统视角。", cs) + '</div><section class="principles-strip page-wrap"><p class="section-kicker">本站只做三件事</p><div><article><span>01</span><h3>讲懂</h3><p>定义、条件、原理和推导不只列结论。</p></article><article><span>02</span><h3>讲通</h3><p>前置知识与相关知识可直接跳转。</p></article><article><span>03</span><h3>讲稳</h3><p>公式专业排版，方法强调条件与检查。</p></article></div></section></main>';
}

function renderSubject(slug) {
  const subject = DATA.subjects.find((item) => item.slug === slug);
  if (!subject) return renderNotFound();
  return '<main class="subject-page page-wrap"><nav class="breadcrumb" aria-label="当前位置">' + nav("home", "首页") + '<span>/</span><strong>' + subject.name + '</strong></nav><header class="page-heading subject-heading"><p class="section-kicker">' + trackLabel(subject.track) + ' · 学科目录</p><h1>' + subject.name + '</h1><p>' + subject.description + '</p><div class="subject-status"><span>' + subject.chapters.length + ' 章目录</span><span>基础精讲＋强化提高</span><span>' + (subject.slug === "gaoshu" ? "第一章正式开放" : "阶段二逐科制作") + '</span></div></header><section class="chapter-directory"><div class="directory-heading"><h2>章节目录</h2><p>目录顺序按讲义主线与数学一 / 408 范围校准；灰色状态表示阶段一仅建立结构。</p></div><ol>' + subject.chapters.map((chapter) =>
    '<li class="' + (chapter.status === "sample" ? "ready" : "planned") + '"><a href="#chapter/' + chapter.slug + '"><span class="chapter-order">' + chapter.number + '</span><div><h3>' + chapter.title + '</h3>' + (chapter.note ? '<p>' + chapter.note + '</p>' : '') + '</div><span class="chapter-state">' + (chapter.status === "sample" ? "基础＋强化已完成" : "目录已建立") + '</span><span aria-hidden="true">→</span></a></li>'
  ).join("") + '</ol></section></main>';
}

function findChapter(slug) {
  for (const subject of DATA.subjects) {
    const chapter = subject.chapters.find((item) => item.slug === slug);
    if (chapter) return { subject, chapter };
  }
}

function renderPlanned(slug) {
  const resolved = findChapter(slug);
  if (!resolved) return renderNotFound();
  const modules = ["章节地图", "考点精讲", "公式与核心结论", "解题方法", "易错点", "复习清单"];
  return '<main class="planned-page page-wrap"><nav class="breadcrumb" aria-label="当前位置">' + nav("home", "首页") + '<span>/</span>' + nav("subject/" + resolved.subject.slug, resolved.subject.name) + '<span>/</span><strong>' + resolved.chapter.number + '</strong></nav><section class="planned-chapter"><p class="section-kicker">阶段一 · 章节模板</p><h1>' + resolved.chapter.title + '</h1><p>本章的独立页面、导航位置和稳定章节 ID 已建立。按照你的验收机制，当前不会提前批量填入正文；高数第一章样板确认后才按既定顺序制作。</p>' + (resolved.chapter.note ? '<aside>' + resolved.chapter.note + '</aside>' : '') + '<div class="planned-modules">' + modules.map((item, index) => '<span><b>' + String(index + 1).padStart(2, "0") + '</b>' + item + '</span>').join("") + '</div><div class="planned-actions">' + nav("chapter/gaoshu-1", "验收高数第一章样板", "primary-button") + nav("subject/" + resolved.subject.slug, "返回学科目录", "secondary-button") + '</div></section></main>';
}

function renderScope() {
  return '<main class="scope-page page-wrap"><nav class="breadcrumb" aria-label="当前位置">' + nav("home", "首页") + '<span>/</span><strong>资料与考纲校准</strong></nav><header class="page-heading"><p class="section-kicker">范围校准 · 2026-08-12</p><h1>先按数学一与 408 的正式范围搭骨架，再把讲义内容放进正确位置。</h1><p>2027 年全国硕士研究生招生考试大纲尚未正式发布，阶段一采用当前可核验的最新官方范围；新大纲发布后只做差异更新，不改变稳定清单 ID。</p></header><section class="scope-grid"><article><span>保留</span><h2>讲义主线</h2><ul><li>高数基础讲义第 5—136 页的九章顺序作为内容主线。</li><li>强化讲义按题型整理的方法信号、条件检查与陷阱。</li><li>第一章的极限定义、计算、存在准则、连续与间断结构。</li></ul></article><article><span>补充</span><h2>数学一缺口</h2><ul><li>第一章补足函数概念、性质、定义域与函数关系建立。</li><li>全站目录补入向量代数与空间解析几何、三重积分、曲线积分与曲面积分。</li><li>无穷级数章补入傅里叶级数与狄利克雷收敛结论。</li></ul></article><article><span>调整</span><h2>内容边界</h2><ul><li>删除讲义中的具体例题与练习，只提炼识别、切入点、步骤和检查。</li><li>不收入数学三经济应用、差分方程等非数学一内容。</li><li>等价代换、洛必达、泰勒等方法补明适用条件，避免只背结论。</li></ul></article></section><section class="source-evidence"><h2>核对依据</h2><p>考试年度与统一命题科目状态以教育部、教育部教育考试院公开信息为准；数学一第一章范围同时与上传讲义中列出的考试内容和考试要求逐项对应。</p><div><a href="https://zszy.neea.edu.cn/html1/report/2509/60-1.htm" target="_blank" rel="noreferrer">教育部教育考试院：2026 年研招工作部署 ↗</a><a href="https://zszy.neea.edu.cn/html1/report/21115/5103-1.htm" target="_blank" rel="noreferrer">教育部教育考试院：数学考试大纲公开页 ↗</a><a href="https://www.moe.gov.cn/s78/A15/s8355/moe_782/tnull_21964.html" target="_blank" rel="noreferrer">教育部：计算机学科统考科目说明 ↗</a></div></section></main>';
}

function renderSearch(params) {
  const query = params.get("q") || "";
  return '<main class="search-page page-wrap"><nav class="breadcrumb" aria-label="当前位置">' + nav("home", "首页") + '<span>/</span><strong>全站搜索</strong></nav><header class="page-heading search-heading"><p class="section-kicker">全站检索</p><h1>直接找到知识点，而不是只找到章节</h1><p>搜索知识点、公式名称、LaTeX 公式、题型方法或正文关键词；正式内容会直达并展开对应位置。</p></header><form id="search-console" class="search-console"><label class="search-main-input"><span aria-hidden="true">⌕</span><input id="search-query" autofocus value="' + esc(query) + '" placeholder="例如：等价无穷小、洛必达、零点定理" aria-label="搜索关键词"><button type="submit">搜索</button></label><div class="search-filters"><label>范围<select id="search-track"><option value="all">数学一＋408</option><option value="math">数学一</option><option value="408">408</option></select></label><label>科目<select id="search-subject"><option value="all">全部科目</option>' + DATA.subjects.map((item) => '<option value="' + item.slug + '">' + item.name + '</option>').join("") + '</select></label><label>层级<select id="search-tab"><option value="all">基础＋强化＋目录</option><option value="foundation">基础精讲</option><option value="advanced">强化提高</option><option value="framework">章节目录</option></select></label></div></form><section class="search-results" aria-live="polite"><div id="search-output"></div></section></main>';
}

function updateSearchResults() {
  const query = document.getElementById("search-query")?.value.trim() || "";
  const track = document.getElementById("search-track")?.value || "all";
  const subject = document.getElementById("search-subject")?.value || "all";
  const tab = document.getElementById("search-tab")?.value || "all";
  const tokens = query.toLowerCase().split(/\s+/).filter(Boolean);
  let results = tokens.length ? DATA.searchIndex.filter((entry) => tokens.every((token) => entry.haystack.includes(token))) : [];
  results = results.filter((entry) => track === "all" || entry.track === track).filter((entry) => subject === "all" || entry.subjectSlug === subject).filter((entry) => tab === "all" || entry.tab === tab).sort((a,b) => Number(b.title.toLowerCase().includes(query.toLowerCase())) - Number(a.title.toLowerCase().includes(query.toLowerCase())));
  const output = document.getElementById("search-output");
  if (!output) return;
  const heading = '<div class="results-heading"><h2>' + (query ? '找到 ' + results.length + ' 条结果' : '输入关键词开始搜索') + '</h2>' + (query ? '<p>结果已按标题命中优先排序。</p>' : '') + '</div>';
  const empty = query && !results.length ? '<div class="empty-search"><strong>暂未找到匹配内容</strong><p>可减少关键词，或切换回“全部科目 / 全部层级”。阶段一只有高数第一章具备正式正文。</p></div>' : '';
  output.innerHTML = heading + empty + '<div class="result-list">' + results.map((entry) => {
    const target = entry.tab === "framework" ? 'chapter/' + entry.chapterSlug : 'chapter/gaoshu-1?tab=' + entry.tab + '&point=' + entry.id + '&q=' + encodeURIComponent(query);
    return '<a class="search-result" href="#' + target + '"><div class="result-meta"><span>' + trackLabel(entry.track) + '</span><span>' + entry.subject + '</span><span>' + entry.chapter + '</span><span>' + entry.tabLabel + '</span></div><h3>' + highlight(entry.title, query) + '</h3><p>' + highlight(entry.excerpt, query) + '</p><strong>定位到对应位置 →</strong></a>';
  }).join("") + '</div>';
}

function pointList(items, query) {
  return '<ul>' + items.map((item) => '<li>' + highlight(item, query) + '</li>').join("") + '</ul>';
}

function formulaList(formulas) {
  if (!formulas?.length) return '';
  return '<div class="formula-list">' + formulas.map((formula) => { const rendered = formula.html || (window.katex ? window.katex.renderToString(formula.latex,{displayMode:true,throwOnError:false,strict:"warn",trust:false}) : '<code>' + esc(formula.latex) + '</code>'); return '<article class="formula-item"><strong>' + esc(formula.name) + '</strong><div class="formula-block" role="math" aria-label="' + esc(formula.latex) + '">' + rendered + '</div>' + (formula.note ? '<p>' + esc(formula.note) + '</p>' : '') + '</article>'; }).join("") + '</div>';
}

function pointCard(point, query, initiallyExpanded) {
  const deep = '<div class="deep-content" ' + (initiallyExpanded ? '' : 'hidden') + '><section><h4>方法路径</h4>' + pointList(point.methods, query) + '</section><section><h4>原理与边界</h4>' + pointList(point.principles, query) + '</section><section class="pitfall-section"><h4>易错点</h4>' + pointList(point.pitfalls, query) + '</section>' + (point.derivation ? '<section class="derivation"><h4>' + esc(point.derivation.title) + '</h4><ol>' + point.derivation.steps.map((step) => '<li>' + highlight(step, query) + '</li>').join("") + '</ol>' + formulaList(point.derivation.formulas) + '</section>' : '') + (point.supplement?.length ? '<section class="supplement-box"><h4>补充说明</h4>' + pointList(point.supplement, query) + '</section>' : '') + (point.related?.length ? '<section class="related-links"><h4>相关知识</h4>' + point.related.map((item) => '<a href="#chapter/gaoshu-1' + item.href + '">' + esc(item.label) + ' →</a>').join("") + '</section>' : '') + '</div>';
  return '<article class="knowledge-card" id="' + point.id + '"><header><p>' + esc(point.eyebrow) + '</p><h2>' + highlight(point.title, query) + '</h2><div class="point-summary">' + highlight(point.summary, query) + '</div></header><div class="knowledge-default"><section><h3>定义与对象</h3>' + pointList(point.definitions, query) + '</section><section><h3>核心结论</h3>' + pointList(point.core, query) + '</section><section><h3>公式与结论</h3>' + formulaList(point.formulas) + '</section></div><button class="expand-button" type="button" data-expand="' + point.id + '" aria-expanded="' + initiallyExpanded + '"><span>' + (initiallyExpanded ? '收起方法、原理与易错点' : '展开方法、原理与易错点') + '</span><span aria-hidden="true">' + (initiallyExpanded ? '−' : '+') + '</span></button>' + deep + '</article>';
}

function readChecklist() {
  try { const value = JSON.parse(localStorage.getItem(storageKey) || "{}"); return value && typeof value === "object" && !Array.isArray(value) ? value : {}; } catch { return {}; }
}

function checklistHtml(items, title) {
  const saved = readChecklist();
  const count = items.filter((item) => saved[item.id]).length;
  return '<section class="checklist-panel" id="review-checklist"><div class="checklist-heading"><div><p class="section-kicker">复习清单</p><h2>' + esc(title) + ' · 当前轮次</h2><p>以核心知识、重要公式和稳定方法为粒度，仅保存在当前设备。</p></div><div class="checklist-count" aria-label="已掌握 ' + count + ' 项，共 ' + items.length + ' 项"><strong>' + count + '</strong><span>/ ' + items.length + '</span></div></div><div class="checklist-items">' + items.map((item) => '<label class="' + (saved[item.id] ? 'checked' : '') + '"><input type="checkbox" data-check="' + item.id + '" ' + (saved[item.id] ? 'checked' : '') + '><span class="checkmark" aria-hidden="true">✓</span><span class="check-kind">' + item.kind + '</span><span>' + esc(item.label) + '</span></label>').join("") + '</div><div class="checklist-tools"><button type="button" id="export-checklist">导出全部清单</button><button type="button" id="import-checklist">导入并合并</button><input id="checklist-file" type="file" accept="application/json,.json" hidden></div><p class="import-message" id="checklist-message" role="status"></p></section>';
}

function tocHtml(tab) {
  return '<p class="toc-label">本轮知识点</p><ol>' + tab.points.map((point) => '<li><button type="button" data-jump="' + point.id + '">' + esc(point.title) + '</button></li>').join("") + '</ol><button class="toc-checklist" type="button" data-jump="review-checklist">复习清单</button>';
}

function renderChapter(params) {
  const tabId = params.get("tab") === "advanced" ? "advanced" : "foundation";
  const pointId = params.get("point") || "";
  const query = params.get("q") || "";
  const tab = DATA.content.tabs.find((item) => item.id === tabId);
  expanded = new Set(pointId ? [pointId] : []);
  const gaoshu = DATA.subjects.find((item) => item.slug === "gaoshu");
  const next = gaoshu.chapters[1];
  return '<div class="reader-shell"><aside class="reader-sidebar">' + nav("subject/gaoshu", "← 高等数学目录", "back-subject") + '<div class="sidebar-tab-name">' + tab.label + '</div>' + tocHtml(tab) + '</aside><main class="chapter-main"><nav class="breadcrumb" aria-label="当前位置">' + nav("home", "首页") + '<span>/</span>' + nav("subject/gaoshu", "高等数学") + '<span>/</span><strong>第一章</strong></nav><button class="mobile-toc-toggle" id="mobile-toc-toggle" type="button" aria-expanded="false"><span>本章目录 · ' + tab.label + '</span><span aria-hidden="true">展开</span></button><div class="mobile-toc" id="mobile-toc" hidden>' + tocHtml(tab) + '</div><header class="chapter-hero"><p class="chapter-number">高等数学 · 第一章</p><h1>' + DATA.content.title + '</h1><p class="chapter-subtitle">' + DATA.content.subtitle + '</p><p class="source-note">' + DATA.content.sourceNote + '</p></header>' + (query ? '<div class="search-arrival" role="status">已从搜索定位到本章，关键词“<mark>' + esc(query) + '</mark>”已高亮；对应知识点已自动展开。</div>' : '') + '<section class="chapter-map" aria-labelledby="chapter-map-title"><div><p class="section-kicker">章节地图</p><h2 id="chapter-map-title">从对象到连续性的四步主线</h2></div><div class="map-steps">' + DATA.content.map.map((item, index) => '<article><span>' + String(index + 1).padStart(2,"0") + '</span><strong>' + item.label + '</strong><p>' + item.detail + '</p></article>').join("") + '</div><div class="key-questions"><strong>学完应能回答</strong>' + pointList(DATA.content.keyQuestions, query) + '</div></section><div class="chapter-tabs" role="tablist" aria-label="基础与强化切换">' + DATA.content.tabs.map((item) => '<button type="button" role="tab" aria-selected="' + (tabId === item.id) + '" class="' + (tabId === item.id ? 'active' : '') + '" data-tab="' + item.id + '"><span>' + item.label + '</span><small>' + (item.id === 'foundation' ? '概念 · 条件 · 基本路径' : '识别 · 组合 · 陷阱') + '</small></button>').join("") + '</div><p class="tab-description">' + tab.description + '</p><div class="knowledge-list">' + tab.points.map((point) => pointCard(point, query, expanded.has(point.id))).join("") + '</div>' + checklistHtml(tab.checklist, DATA.content.title + ' · ' + tab.label) + '<nav class="chapter-next" aria-label="章节导航"><span>已经是本学科第一章</span>' + nav("subject/gaoshu", "返回高数目录") + '<span>' + nav("chapter/" + next.slug, next.title + " →") + '</span></nav></main><nav class="mobile-bottom-nav" aria-label="手机章节导航"><span>上一章</span>' + nav("subject/gaoshu", "目录") + '<span>' + nav("chapter/" + next.slug, "下一章") + '</span></nav></div>';
}

function renderNotFound() {
  return '<main class="planned-page page-wrap"><section class="planned-chapter"><p class="section-kicker">页面未找到</p><h1>这个位置还没有内容</h1><div class="planned-actions">' + nav("home", "返回首页", "primary-button") + '</div></section></main>';
}

function bindSearch() {
  const form = document.getElementById("search-console");
  if (!form) return;
  form.addEventListener("submit", (event) => { event.preventDefault(); const query = document.getElementById("search-query").value.trim(); location.hash = query ? "search?q=" + encodeURIComponent(query) : "search"; updateSearchResults(); });
  for (const id of ["search-query","search-track","search-subject","search-tab"]) document.getElementById(id)?.addEventListener(id === "search-query" ? "input" : "change", updateSearchResults);
  updateSearchResults();
}

function bindChapter(params) {
  const tabId = params.get("tab") === "advanced" ? "advanced" : "foundation";
  document.querySelectorAll("[data-tab]").forEach((button) => button.addEventListener("click", () => { location.hash = "chapter/gaoshu-1?tab=" + button.dataset.tab; }));
  document.querySelectorAll("[data-expand]").forEach((button) => button.addEventListener("click", () => {
    const id = button.dataset.expand; const card = document.getElementById(id); const deep = card.querySelector(".deep-content"); const open = deep.hasAttribute("hidden");
    if (open) { deep.removeAttribute("hidden"); expanded.add(id); } else { deep.setAttribute("hidden", ""); expanded.delete(id); }
    button.setAttribute("aria-expanded", String(open)); button.firstElementChild.textContent = open ? "收起方法、原理与易错点" : "展开方法、原理与易错点"; button.lastElementChild.textContent = open ? "−" : "+";
  }));
  document.querySelectorAll("[data-jump]").forEach((button) => button.addEventListener("click", () => {
    const id = button.dataset.jump; const target = document.getElementById(id); if (!target) return;
    const expandButton = target.querySelector("[data-expand]"); if (expandButton && target.querySelector(".deep-content")?.hasAttribute("hidden")) expandButton.click();
    document.getElementById("mobile-toc")?.setAttribute("hidden", ""); target.scrollIntoView({behavior:"smooth",block:"start"});
  }));
  document.getElementById("mobile-toc-toggle")?.addEventListener("click", (event) => {
    const menu = document.getElementById("mobile-toc"); const open = menu.hasAttribute("hidden"); if (open) menu.removeAttribute("hidden"); else menu.setAttribute("hidden", "");
    event.currentTarget.setAttribute("aria-expanded", String(open)); event.currentTarget.lastElementChild.textContent = open ? "收起" : "展开";
  });
  document.querySelectorAll("[data-check]").forEach((input) => input.addEventListener("change", () => {
    const saved = readChecklist(); saved[input.dataset.check] = input.checked; localStorage.setItem(storageKey, JSON.stringify(saved));
    input.closest("label")?.classList.toggle("checked", input.checked);
    const tab = DATA.content.tabs.find((item) => item.id === tabId); const count = tab.checklist.filter((item) => saved[item.id]).length; document.querySelector(".checklist-count strong").textContent = String(count);
  }));
  document.getElementById("export-checklist")?.addEventListener("click", () => {
    const payload = {format:checklistFormat,version:1,exportedAt:new Date().toISOString(),checked:readChecklist()}; const blob = new Blob([JSON.stringify(payload,null,2)],{type:"application/json;charset=utf-8"}); const url = URL.createObjectURL(blob); const link = document.createElement("a"); link.href=url; link.download="宇的考研复习清单_"+new Date().toISOString().slice(0,10)+".json"; link.click(); URL.revokeObjectURL(url); document.getElementById("checklist-message").textContent="清单数据已导出。可在另一台设备上导入并合并。";
  });
  const fileInput = document.getElementById("checklist-file"); document.getElementById("import-checklist")?.addEventListener("click",()=>fileInput.click()); fileInput?.addEventListener("change",async()=>{
    const file=fileInput.files?.[0]; fileInput.value=""; if(!file)return; const message=document.getElementById("checklist-message"); try { const parsed=JSON.parse(await file.text()); if(parsed.format!==checklistFormat||parsed.version!==1||!parsed.checked||typeof parsed.checked!=="object"||Array.isArray(parsed.checked)||Object.entries(parsed.checked).some(([id,value])=>!id||typeof value!=="boolean")) throw new Error("文件格式或记录不合法"); const saved=readChecklist(); for(const [id,value] of Object.entries(parsed.checked)) if(value)saved[id]=true; localStorage.setItem(storageKey,JSON.stringify(saved)); message.textContent="导入成功：已与本机记录合并，没有覆盖原有勾选。"; setTimeout(renderApp,200); } catch(error) { message.textContent="导入失败："+(error?.message||"无法读取文件")+"。现有记录未改变。"; }
  });
  const point = params.get("point"); if (point) requestAnimationFrame(() => setTimeout(() => document.getElementById(point)?.scrollIntoView({behavior:"smooth",block:"start"}), 80));
}

function renderApp() {
  const { path, params } = parseRoute();
  if (path === "home") app.innerHTML = renderHome();
  else if (path === "scope") app.innerHTML = renderScope();
  else if (path === "search") app.innerHTML = renderSearch(params);
  else if (path.startsWith("subject/")) app.innerHTML = renderSubject(path.split("/")[1]);
  else if (path === "chapter/gaoshu-1") app.innerHTML = renderChapter(params);
  else if (path.startsWith("chapter/")) app.innerHTML = renderPlanned(path.split("/")[1]);
  else app.innerHTML = renderNotFound();
  if (path === "search") bindSearch();
  if (path === "chapter/gaoshu-1") bindChapter(params);
  if (!params.get("point")) window.scrollTo(0,0);
}

document.getElementById("header-search").addEventListener("submit", (event) => { event.preventDefault(); const query = new FormData(event.currentTarget).get("q")?.toString().trim() || ""; location.hash = query ? "search?q=" + encodeURIComponent(query) : "search"; });
const sizeButtons = document.querySelectorAll("[data-size]"); const savedSize = localStorage.getItem("yu-kaoyan-font-size") || "standard"; document.documentElement.dataset.fontSize = savedSize; sizeButtons.forEach((button) => { button.classList.toggle("active",button.dataset.size===savedSize); button.addEventListener("click",()=>{ document.documentElement.dataset.fontSize=button.dataset.size; localStorage.setItem("yu-kaoyan-font-size",button.dataset.size); sizeButtons.forEach((item)=>item.classList.toggle("active",item===button)); }); });
window.addEventListener("hashchange", renderApp);
renderApp();
