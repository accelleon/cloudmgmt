/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Account } from './Account';

export type BillingPeriod = {
    start_date: string;
    end_date: string;
    total: number;
    balance: number;
    account_id: number;
    id: number;
    account: Account;
};
