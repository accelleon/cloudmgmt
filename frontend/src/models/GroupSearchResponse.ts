/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Group } from './Group';
import type { SearchOrder } from './SearchOrder';

export type GroupSearchResponse = {
    results: Array<Group>;
    page: number;
    per_page: number;
    total: number;
    order: SearchOrder;
    next?: string;
    prev?: string;
};
