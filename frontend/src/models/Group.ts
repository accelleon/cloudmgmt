/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Account } from './Account';

export type Group = {
    id: number;
    name: string;
    accounts: Array<Account>;
};
