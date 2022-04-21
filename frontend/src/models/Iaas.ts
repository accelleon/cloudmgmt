/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { IaasParam } from './IaasParam';
import type { IaasType } from './IaasType';

export type Iaas = {
    name: string;
    type: IaasType;
    params: Array<IaasParam>;
    id: number;
};
