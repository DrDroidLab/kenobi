import { transformToQueryBuilderPayload } from '../../utils/utils';

export const transformToMTQueryBuilderPayload = (
  default_query_request,
  options,
  attrOptionType,
  idName
) => {
  const transformedPayload = transformToQueryBuilderPayload(
    default_query_request,
    options,
    attrOptionType
  );
  for (let i = 0; i < transformedPayload.filters.length; i++) {
    const filter = transformedPayload.filters[i];
    if (filter.lhs === idName) {
      filter.hide = true;
    }
  }
  return transformedPayload;
};
