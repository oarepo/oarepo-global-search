import {
  createSearchAppsInit,
  parseSearchAppConfigs,
  DynamicResultsListItem,
} from "@js/oarepo_ui";

const [{ overridableIdPrefix }] = parseSearchAppConfigs();

export const componentOverrides = {
  [`${overridableIdPrefix}.ResultsList.item`]: DynamicResultsListItem,
};

createSearchAppsInit({ componentOverrides });
