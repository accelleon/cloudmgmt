/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Account } from './Account';
import type { SearchOrder } from './SearchOrder';

export type AccountSearchResponse = {
    results: Array<Account>;
    page: number;
    per_page: number;
    total: number;
    order: SearchOrder;
    next?: string;
    prev?: string;
};
