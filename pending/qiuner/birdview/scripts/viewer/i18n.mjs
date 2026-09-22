// Generated from src/viewer/i18n.mts. Do not edit directly.

// src/viewer/i18n.mts
var uiTranslations = {
  "\u67B6\u6784\u6807\u8BC6": "Architecture identity",
  "\u524D\u7AEF": "Frontend",
  "\u540E\u7AEF": "Backend",
  "\u7F13\u5B58": "Cache",
  "\u6570\u636E\u5B58\u50A8": "Data store",
  "\u4EFB\u52A1\u4E0E\u961F\u5217": "Tasks / Queue",
  "\u5B89\u5168": "Security",
  "\u901A\u7528\u6A21\u5757": "Generic",
  "\u5173\u95ED\u8BE6\u60C5": "Close details",
  "\u67E5\u770B\u8BE6\u60C5": "Inspect module",
  "\u770B\u89C1 AI \u5982\u4F55\u6539\u53D8\u4F60\u7684\u7CFB\u7EDF": "See how AI changes your system",
  "\u67B6\u6784\u5FEB\u7167": "Architecture snapshot",
  "\u7CFB\u7EDF\u67B6\u6784": "System architecture",
  "\u9879\u76EE\u67B6\u6784": "Project architecture",
  "\u7F29\u5C0F": "Zoom out",
  "\u653E\u5927": "Zoom in",
  "\u7F29\u653E\u6BD4\u4F8B": "Zoom level",
  "\u9002\u914D\u5168\u56FE": "Fit diagram",
  "\u539F\u59CB\u5927\u5C0F": "Actual size",
  "\u6A21\u5757\u5173\u7CFB": "Module relationships",
  "\u67B6\u6784\u5FEB\u7167 \xB7 \u5C1A\u65E0\u4FEE\u6539\u6D3B\u52A8": "Architecture snapshot \xB7 No change activity",
  "\u6A21\u5757\u8BE6\u60C5": "Module details",
  "\u6587\u4EF6\u5F52\u5C5E": "File ownership",
  "\u6E90\u7801\u8BC1\u636E": "Source evidence",
  "\u5F85\u786E\u8BA4": "Uncertain",
  "\u76F8\u5173\u8FDE\u63A5": "Related connections",
  "\u5207\u6362\u5230\u6DF1\u8272": "Switch to dark theme",
  "\u5207\u6362\u5230\u6D45\u8272": "Switch to light theme",
  "\u5173\u7CFB\u65B9\u5411\u52A8\u753B\uFF0C\u4E0D\u4EE3\u8868\u5B9E\u65F6\u6570\u636E\u4F20\u8F93": "Relationship direction, not live data transfer",
  "\u6D41\u5411": "Flow",
  "\u5916\u90E8\u670D\u52A1": "External service",
  "\u672C\u5730\u6A21\u5757": "Local module",
  "\u6709\u6765\u6E90\u8BC1\u636E": "Source-backed",
  "\u65E0\u672C\u5730\u6587\u4EF6\u5F52\u5C5E": "No local file ownership",
  "\u65E0\u6765\u6E90\u8BC1\u636E": "No source evidence",
  "\u65E0\u5DF2\u8BB0\u5F55\u7684\u5F85\u786E\u8BA4\u9879": "No recorded open questions",
  "\u65E0\u5DF2\u8BB0\u5F55\u7684\u5173\u7CFB": "No recorded relationships"
};
function availableLanguages(map) {
  const languages = /* @__PURE__ */ new Set([map.language || "zh", "zh", "en"]);
  for (const item of [map.project, ...map.modules, ...map.relationships, ...map.groups || [], ...map.constraints || []]) {
    for (const locale of Object.keys(item.translations || {})) languages.add(locale);
    for (const source of item.evidence || []) for (const locale of Object.keys(source.translations || {})) languages.add(locale);
  }
  return languages;
}
function selectLanguage(base, available, stored, requested) {
  let language = base || "zh";
  if (stored !== null && available.has(stored)) language = stored;
  if (requested !== null && available.has(requested)) language = requested;
  return language;
}
var isChinese = (language) => language.split("-")[0] === "zh";
var translate = (text, language) => isChinese(language) ? text : uiTranslations[text] || text;
function localized(item, field, language) {
  return item.translations?.[language]?.[field] ?? item[field] ?? "";
}
export {
  availableLanguages,
  isChinese,
  localized,
  selectLanguage,
  translate,
  uiTranslations
};
