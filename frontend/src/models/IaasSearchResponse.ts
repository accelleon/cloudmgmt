/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Iaas } from './Iaas';
import type { SearchOrder } from './SearchOrder';

export type IaasSearchResponse = {
    results: Array<Iaas>;
    page: number;
    per_page: number;
    total: number;
    order: SearchOrder;
    next?: string;
    prev?: string;
};
