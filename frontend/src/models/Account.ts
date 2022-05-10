/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { _Iaas } from './_Iaas';
import type { AccountData } from './AccountData';

export type Account = {
    id?: number;
    name: string;
    iaas_id: number;
    currency: string;
    data: AccountData;
    validated: boolean;
    last_error?: string;
    iaas: _Iaas;
};
