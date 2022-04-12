/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { _Account } from './_Account';
import type { IaasType } from './IaasType';

export type Iaas = {
    name: string;
    type: IaasType;
    params: Array<string>;
    id: number;
    accounts: Array<_Account>;
};
