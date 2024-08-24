import {
  createSearchAppsInit,
  parseSearchAppConfigs,
  SearchappSearchbarElement,
  DynamicResultsListItem,
} from "@js/oarepo_ui";

const [{ overridableIdPrefix }] = parseSearchAppConfigs();

export const componentOverrides = {
  [`${overridableIdPrefix}.SearchBar.element`]: SearchappSearchbarElement,
  [`${overridableIdPrefix}.ResultsList.item`]: DynamicResultsListItem,
};

createSearchAppsInit({ componentOverrides });
