/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BillingPeriod } from './BillingPeriod';
import type { SearchOrder } from './SearchOrder';

export type BillingSearchResponse = {
    results: Array<BillingPeriod>;
    page: number;
    per_page: number;
    total: number;
    order: SearchOrder;
    next?: string;
    prev?: string;
};
