/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SearchOrder } from './SearchOrder';
import type { User } from './User';

export type UserSearchResponse = {
    results: Array<User>;
    page: number;
    per_page: number;
    total: number;
    order: SearchOrder;
    next?: string;
    prev?: string;
};
