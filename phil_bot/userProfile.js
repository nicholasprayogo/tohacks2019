// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

class UserProfile {
    constructor(withdraw, usedebit, age, paymentmethod, student) {
        this.withdraw = withdraw;
        this.usedebit = usedebit;
        this.age = age;
        this.paymentmethod = paymentmethod;
        this.student = student;
    }
}

module.exports.UserProfile = UserProfile;
