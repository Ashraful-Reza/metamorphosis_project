/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
export class BOMTransferController extends ListController {
   setup() {
      super.setup();
   }
   willStart() {
      super.willStart();
      this.model.root.on('record-editable-saved', this, this.onWizardClosed);
   }
   OnTBClick() {
       this.actionService.doAction({
         type: 'ir.actions.act_window',
         res_model: 'bom.transfer.wizard',
         name:'Date',
         view_mode: 'form',
         view_type: 'form',
         views: [[false, 'form']],
         target: 'new',
         res_id: false,
      });
   }
   async onWizardClosed(payload) {
      if (payload.props.closedReason === 'apply') {
         const domain = payload.props.data.domain;
         this.model.root.query.updateDomain([domain]);
      }
   }
}
registry.category("views").add("bom_transfer", {
   ...listView,
   Controller: BOMTransferController,
   buttonTemplate: "meta_bom_transfer_process.ListView.Buttons",
});